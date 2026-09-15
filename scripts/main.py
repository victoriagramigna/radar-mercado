"""
Punto de entrada principal del Radar de Mercado (v2).
Suma al pipeline original: historial persistente, régimen de mercado (VIX),
estados narrativos con confirmación con demora, VCP, RSI semanal, stop-loss.
"""
import json
import logging
import os
from datetime import datetime, timezone

from config import TICKERS, BENCHMARK, SCORE_MINIMO_ALERTA, MODO, VIX_TICKER
from datos import traer_datos
from rs_score import calcular_rs_score
from alertas import detectar_alertas
from contexto import escanear_titulares, evaluar_contexto_macro, recomendacion_final
from regimen_mercado import evaluar_regimen_mercado
from historial import cargar_historial, guardar_historial
from telegram_bot import notificar_alertas
from macro_local import traer_contexto_macro
from frescura import evaluar_frescura

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("radar.main")


def traer_titulares_ejemplo():
    """Placeholder -- se conecta Finnhub /news más adelante."""
    return []


def traer_vix(precios: dict):
    """El VIX ya viene traído junto con el resto en datos.py si se agrega
    al diccionario de tickers a pedir -- ver main() más abajo."""
    if VIX_TICKER in precios and not precios[VIX_TICKER].empty:
        return float(precios[VIX_TICKER].iloc[-1])
    return None


def main():
    log.info(f"=== Radar de Mercado — corrida iniciada (modo={MODO}) ===")
    timestamp = datetime.now(timezone.utc).isoformat()
    fecha_hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")

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

    # 2b. Frescura del dato -- detecta si el gap desde el último dato es
    # más grande que un feriado común (podría indicar una fuente rota)
    ultima_fecha_benchmark = precios[BENCHMARK].dropna().index[-1] if not precios[BENCHMARK].dropna().empty else None
    frescura = evaluar_frescura(ultima_fecha_benchmark)
    log.info(f"Frescura del dato: {frescura}")

    # 3. RS Score
    df_rs = calcular_rs_score(precios, TICKERS, BENCHMARK)
    rs_por_sector = df_rs.groupby("Sector")["RS_Score"].mean().to_dict() if not df_rs.empty else {}

    # 4. Historial persistente (para confirmación con demora y stop-loss)
    historial = cargar_historial()

    # 5. Alertas técnicas (v2: score 0-7, estados narrativos, VCP, RSI semanal)
    df_alertas, historial = detectar_alertas(precios, volumenes, TICKERS, BENCHMARK,
                                              rs_por_sector, historial, fecha_hoy)
    guardar_historial(historial)

    # 6. Contexto (noticias + macro-local)
    titulares = traer_titulares_ejemplo()  # Finnhub -- pendiente de conectar
    alertas_sector = escanear_titulares(titulares)
    riesgo_pais, riesgo_pais_ayer, brecha = traer_contexto_macro()  # ArgentinaDatos -- real
    contexto_macro = evaluar_contexto_macro(riesgo_pais, riesgo_pais_ayer, brecha)
    log.info(f"Contexto macro-local: {contexto_macro}")

    # 7. Recomendación final -- ahora también ajustada por el régimen de mercado (VIX)
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
        "tickers_ok": len(precios) - 2,  # -1 benchmark, -1 VIX
        "tickers_fallidos": fallidos,
        "frescura_dato": frescura,
        "ranking": df_rs.to_dict(orient="records") if not df_rs.empty else [],
        "rs_por_sector": rs_por_sector,
        "regimen_mercado": regimen,
        "alertas": recomendaciones,
        "contexto_macro": contexto_macro,
    }

    with open("data/ultimo.json", "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    log.info("Guardado en data/ultimo.json")

    # 9. Notificaciones (con deduplicación: no repetir la misma alerta/estado el mismo día)
    alertas_relevantes = [a for a in recomendaciones if a.get("Score_num") and a["Score_num"] >= SCORE_MINIMO_ALERTA]
    historial.setdefault("_notificaciones", {})
    alertas_nuevas = []
    for a in alertas_relevantes:
        ticker = a["Ticker"]
        clave_estado = f"{fecha_hoy}|{a['Estado']}"
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
