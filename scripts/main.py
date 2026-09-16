"""
Punto de entrada principal del Radar de Mercado (v3).
Suma sobre v2: RSI/RVOL/SMA200 expuestos para todo el universo (no solo
alertas), fix del bug de expiración de alertas (ventana de 48hs), nueva
señal "líder apoyando en soporte", y estimación de próxima corrida (para
que sea más fácil distinguir "no corrió todavía" de "corrió y no hubo
novedades").
"""
import json
import logging
import os
from datetime import datetime, timezone, timedelta

from config import (TICKERS, BENCHMARK, SCORE_MINIMO_ALERTA, MODO, VIX_TICKER,
                     UMBRAL_MOVIMIENTO_DIARIO_PCT)
from datos import traer_datos
from rs_score import calcular_rs_score
from alertas import detectar_alertas
from contexto import escanear_titulares, evaluar_contexto_macro, recomendacion_final
from regimen_mercado import evaluar_regimen_mercado
from historial import cargar_historial, guardar_historial
from telegram_bot import notificar_alertas
from macro_local import traer_contexto_macro
from frescura import evaluar_frescura
from cedear_pricing import calcular_brechas_cedear
from movimientos import detectar_movimientos_diarios

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("radar.main")


def traer_titulares_ejemplo():
    """Placeholder -- se conecta Finnhub /news más adelante."""
    return []


def traer_vix(precios: dict):
    if VIX_TICKER in precios and not precios[VIX_TICKER].empty:
        return float(precios[VIX_TICKER].iloc[-1])
    return None


def estimar_proxima_corrida(ahora: datetime) -> str:
    """
    Estimación INFORMATIVA de la próxima corrida programada, según el cron
    (cada hora en punto de 14 a 21 UTC, lunes a viernes). GitHub Actions
    corre los crons en modo "best effort" -- puede demorarse minutos u
    horas en momentos de alta demanda de su infraestructura compartida
    gratuita, así que esto es una referencia, no una garantía exacta.
    """
    candidato = ahora.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    for _ in range(24 * 8):  # tope de seguridad, no debería iterar tanto
        es_habil = candidato.weekday() < 5  # 0=lunes ... 4=viernes
        en_horario = 14 <= candidato.hour <= 21
        if es_habil and en_horario:
            return candidato.isoformat()
        candidato += timedelta(hours=1)
    return None  # no debería pasar nunca, pero mejor no romper si pasa


def main():
    log.info(f"=== Radar de Mercado — corrida iniciada (modo={MODO}) ===")
    ahora = datetime.now(timezone.utc)
    timestamp = ahora.isoformat()
    fecha_hoy = ahora.strftime("%Y-%m-%d")

    # 1. Datos (se pide también el VIX, sumándolo como si fuera un ticker más)
    tickers_a_pedir = {**TICKERS}
    precios, volumenes, fallidos = traer_datos({**tickers_a_pedir, VIX_TICKER: "Índice"}, BENCHMARK)
    if BENCHMARK not in precios:
        log.error("El benchmark no se pudo traer -- abortando la corrida")
        return

    # 2. Régimen de mercado (VIX)
    vix_actual = traer_vix(precios)
    regimen = evaluar_regimen_mercado(vix_actual)
    log.info(f"Régimen de mercado: {regimen}")

    # 2b. Frescura del dato
    ultima_fecha_benchmark = precios[BENCHMARK].dropna().index[-1] if not precios[BENCHMARK].dropna().empty else None
    frescura = evaluar_frescura(ultima_fecha_benchmark)
    log.info(f"Frescura del dato: {frescura}")

    # 3. RS Score + indicadores completos (RSI, RVOL, SMA50/200) para TODO el universo
    df_rs = calcular_rs_score(precios, TICKERS, BENCHMARK, volumenes)
    rs_por_sector = df_rs.groupby("Sector")["RS_Score"].mean().to_dict() if not df_rs.empty else {}
    rs_por_ticker = dict(zip(df_rs["Ticker"], df_rs["RS_Score"])) if not df_rs.empty else {}

    # 3b. Señal de CEDEAR caro/barato
    precios_usd_actuales = dict(zip(df_rs["Ticker"], df_rs["Precio"])) if not df_rs.empty else {}
    cedears_pricing = calcular_brechas_cedear(precios_usd_actuales)
    log.info(f"CEDEARs -- CCL: {cedears_pricing.get('ccl')}, "
             f"{len(cedears_pricing.get('cedears', []))} calculados")

    # 3c. Panel de movimientos diarios inusuales
    movimientos_dia = detectar_movimientos_diarios(precios, TICKERS)
    log.info(f"Movimientos del día: {len(movimientos_dia)} ticker(s) con variación >= "
             f"{UMBRAL_MOVIMIENTO_DIARIO_PCT}%")

    # 4. Historial persistente
    historial = cargar_historial()

    # 5. Alertas técnicas (v3: expiran a las 48hs, + señal "líder en soporte")
    df_alertas, historial = detectar_alertas(precios, volumenes, TICKERS, BENCHMARK,
                                              rs_por_sector, rs_por_ticker, historial,
                                              fecha_hoy, timestamp)
    guardar_historial(historial)

    # 6. Contexto (noticias + macro-local)
    titulares = traer_titulares_ejemplo()  # Finnhub -- pendiente de conectar
    alertas_sector = escanear_titulares(titulares)
    riesgo_pais, riesgo_pais_ayer, brecha = traer_contexto_macro()  # ArgentinaDatos -- real
    contexto_macro = evaluar_contexto_macro(riesgo_pais, riesgo_pais_ayer, brecha)
    log.info(f"Contexto macro-local: {contexto_macro}")

    # 7. Recomendación final
    recomendaciones = []
    for _, fila in df_alertas.iterrows():
        rec = recomendacion_final(fila["Sector"], fila["Score_num"], fila["Estado"],
                                   alertas_sector, contexto_macro)
        if not regimen.get("sin_datos") and not regimen.get("sano") and rec["Recomendación final"] == "COMPRA":
            rec["Recomendación final"] = "MANTENER"
            rec["Ajustado por"] += f"; régimen de mercado volátil ({regimen['motivo']})"
        recomendaciones.append({**fila.to_dict(), **rec})

    # 8. Guardar resultado para el dashboard
    salida = {
        "generado_utc": timestamp,
        "proxima_corrida_estimada_utc": estimar_proxima_corrida(ahora),
        "tickers_ok": len(precios) - 2,  # -1 benchmark, -1 VIX
        "tickers_fallidos": fallidos,
        "frescura_dato": frescura,
        "ranking": df_rs.to_dict(orient="records") if not df_rs.empty else [],
        "rs_por_sector": rs_por_sector,
        "regimen_mercado": regimen,
        "alertas": recomendaciones,
        "contexto_macro": contexto_macro,
        "cedears_pricing": cedears_pricing,
        "movimientos_dia": movimientos_dia,
    }

    with open("data/ultimo.json", "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    log.info("Guardado en data/ultimo.json")

    # 9. Notificaciones (dedup por día+estado; "líder en soporte" no usa la escala 0-7)
    alertas_relevantes = [
        a for a in recomendaciones
        if (a.get("Score_num") and a["Score_num"] >= SCORE_MINIMO_ALERTA) or a.get("Tipo") == "lider_soporte"
    ]
    historial.setdefault("_notificaciones", {})
    alertas_nuevas = []
    for a in alertas_relevantes:
        ticker = a["Ticker"]
        clave_estado = f"{fecha_hoy}|{a['Tipo']}|{a['Estado']}"
        ya_notificado = historial["_notificaciones"].get(ticker) == clave_estado
        if not ya_notificado:
            alertas_nuevas.append(a)
            historial["_notificaciones"][ticker] = clave_estado

    if alertas_relevantes:
        log.info(f"{len(alertas_relevantes)} alerta(s) relevante(s), {len(alertas_nuevas)} nueva(s) (no notificadas aún hoy)")

    if alertas_nuevas:
        if MODO == "produccion":
            token = os.environ.get("TELEGRAM_BOT_TOKEN")
            chat_id = os.environ.get("TELEGRAM_CHAT_ID")
            enviados = notificar_alertas(token, chat_id, alertas_nuevas, fecha_hoy)
            log.info(f"MODO=produccion -- {enviados} mensaje(s) enviado(s) a Telegram")
        else:
            log.info("MODO=test -- NO se envían notificaciones reales, solo se loguea")
            for a in alertas_nuevas:
                log.info(f"  [TEST] {a['Ticker']}: {a['Estado']} ({a['Score']}) — {a['Recomendación final']}")
    else:
        log.info("Sin alertas nuevas para notificar en esta corrida")

    guardar_historial(historial)

    log.info("=== Corrida finalizada ===")


if __name__ == "__main__":
    main()
