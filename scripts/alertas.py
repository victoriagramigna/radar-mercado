"""
Sistema de alertas técnicas v2.
Score de Confirmación ampliado a 7 puntos posibles:
  cruce SMA50, volumen fuerte, RSI diario sano, base ordenada,
  sector+mercado ok, VCP válido (pilar "Setup"), RSI semanal cruzando alcista.

Cada señal viene con un ESTADO NARRATIVO (no reemplaza el score, lo acompaña),
con confirmación con demora: una señal recién detectada no salta a "confirmado"
de golpe -- necesita sostenerse DIAS_CONFIRMACION días o hacer nuevo máximo.
Esto requiere el historial persistente (historial.py) entre corridas.

También detecta stop-loss: si un ticker que veníamos confirmando pierde su
EMA200, se dispara alerta de salida, independientemente del score de entrada.
"""
import pandas as pd
from config import (VOLUMEN_RELATIVO_MINIMO, RSI_ZONA_SANA, VENTANA_BASE_DIAS,
                     SMA_CORTAS, EMA_LARGA, DIAS_CONFIRMACION, SCORE_TECHO_SIN_CONFIRMAR,
                     ESTADOS)
from vcp import detectar_vcp


def rsi(serie, periodo=14):
    delta = serie.diff()
    ganancia = delta.clip(lower=0).rolling(periodo).mean()
    perdida = (-delta.clip(upper=0)).rolling(periodo).mean()
    rs = ganancia / perdida
    return 100 - (100 / (1 + rs))


def rsi_semanal_cruzando(close_diario: pd.Series) -> bool:
    """Resamplea a semanal y chequea si el RSI(14) semanal cruzó su propia
    media móvil de 14 semanas hacia arriba en la última semana cerrada."""
    semanal = close_diario.resample("W").last().dropna()
    if len(semanal) < 30:
        return False
    rsi_sem = rsi(semanal, 14)
    rsi_sem_media = rsi_sem.rolling(14).mean()
    if len(rsi_sem) < 2 or rsi_sem_media.isna().iloc[-2:].any():
        return False
    cruzo = (rsi_sem.iloc[-2] <= rsi_sem_media.iloc[-2]) and (rsi_sem.iloc[-1] > rsi_sem_media.iloc[-1])
    return bool(cruzo)


def detectar_alertas(precios: dict, volumenes: dict, tickers_sector: dict, benchmark: str,
                      rs_por_sector: dict, historial: dict, fecha_hoy: str):
    bench = precios[benchmark].dropna()
    bench_sma50 = bench.rolling(50).mean()
    bench_sobre_sma50 = bool(bench.iloc[-1] > bench_sma50.iloc[-1])

    alertas = []
    for ticker, sector in tickers_sector.items():
        if ticker not in precios or ticker not in volumenes:
            continue
        close = precios[ticker].dropna()
        vol = volumenes[ticker].dropna()
        if len(close) < 200:
            continue

        sma_cortas = {n: close.rolling(n).mean() for n in SMA_CORTAS}  # SMA10, SMA21, SMA50
        sma50 = sma_cortas[50]
        ema200 = close.ewm(span=EMA_LARGA, adjust=False).mean()
        rsi14 = rsi(close, 14)
        vol_prom20 = vol.rolling(20).mean()
        max_52w = close.iloc[-252:].max() if len(close) >= 252 else close.max()

        precio_hoy, precio_ayer = close.iloc[-1], close.iloc[-2]
        sma50_hoy, sma50_ayer = sma50.iloc[-1], sma50.iloc[-2]
        ema200_hoy = ema200.iloc[-1]
        vol_rel_hoy = vol.iloc[-1] / vol_prom20.iloc[-1] if vol_prom20.iloc[-1] > 0 else 1
        rsi_hoy = rsi14.iloc[-1]

        # --- Señales base (ya validadas) ---
        cruzo_sma50_hoy = (precio_ayer <= sma50_ayer) and (precio_hoy > sma50_hoy)
        rompio_piso = (precio_hoy < ema200_hoy) and (precio_ayer >= ema200.iloc[-2])
        volumen_confirma = vol_rel_hoy > VOLUMEN_RELATIVO_MINIMO
        rsi_sano = RSI_ZONA_SANA[0] <= rsi_hoy <= RSI_ZONA_SANA[1]
        vol_reciente = close.iloc[-VENTANA_BASE_DIAS:].pct_change().std()
        vol_historica = close.pct_change().std()
        base_ordenada = vol_reciente < vol_historica * 0.85
        sector_acompana = rs_por_sector.get(sector, 0) > 50 and bench_sobre_sma50

        # --- Señales nuevas ---
        vcp_resultado = detectar_vcp(close, vol)  # pilar "Setup"
        rsi_sem_cruzo = rsi_semanal_cruzando(close)
        nuevo_max_52w = precio_hoy >= max_52w * 0.999  # tolerancia por redondeo

        # --- Stop-loss: independiente del cruce, mira historial previo ---
        estado_previo = historial.get(ticker, {})
        venia_confirmado = estado_previo.get("estado") == "confirmado"
        alerta_stop_loss = venia_confirmado and rompio_piso

        # --- Score (0-7) ---
        score, señales = 0, []
        if cruzo_sma50_hoy:
            score += 1; señales.append("cruce SMA50")
        if volumen_confirma:
            score += 1; señales.append("volumen fuerte")
        if rsi_sano:
            score += 1; señales.append("RSI diario sano")
        if base_ordenada:
            score += 1; señales.append("base ordenada")
        if sector_acompana:
            score += 1; señales.append("sector+mercado ok")
        if vcp_resultado["valido"]:
            score += 1; señales.append(f"VCP válido ({vcp_resultado['contracciones_detectadas']} contracciones)")
        if rsi_sem_cruzo:
            score += 1; señales.append("RSI semanal cruzó alcista")

        # --- Confirmación con demora: trackea días verdes consecutivos desde el cruce ---
        dias_verdes = estado_previo.get("dias_verdes_consecutivos", 0)
        if cruzo_sma50_hoy:
            dias_verdes = 1  # el cruce mismo cuenta como día 1
        elif estado_previo.get("estado") in ("recien_cruzo", "sacudon") and precio_hoy > precio_ayer:
            dias_verdes += 1
        elif estado_previo.get("estado") in ("recien_cruzo", "sacudon") and precio_hoy <= precio_ayer:
            dias_verdes = 0  # se cortó la racha -> sacudón

        confirmado = dias_verdes >= DIAS_CONFIRMACION or nuevo_max_52w

        # --- Determinar estado narrativo ---
        estado_key = None
        if alerta_stop_loss:
            estado_key = "stop_loss"
        elif rompio_piso:
            estado_key = "deterioro"
        elif cruzo_sma50_hoy or estado_previo.get("estado") in ("recien_cruzo", "sacudon", "confirmado"):
            if confirmado and volumen_confirma and nuevo_max_52w:
                estado_key = "ruptura_vol"
            elif confirmado:
                estado_key = "confirmado"
            elif dias_verdes == 0 and not cruzo_sma50_hoy:
                estado_key = "sacudon"
            else:
                estado_key = "recien_cruzo"

        # Score mostrado: si todavía no confirmó, se topea (evita mostrar 6/7 el mismo
        # día del cruce sin haber sostenido nada)
        score_mostrado = score
        if estado_key in ("recien_cruzo", "sacudon"):
            score_mostrado = min(score, SCORE_TECHO_SIN_CONFIRMAR)

        # Actualizar historial para la próxima corrida
        historial[ticker] = {
            "ultima_fecha": fecha_hoy,
            "estado": estado_key,
            "dias_verdes_consecutivos": dias_verdes,
            "precio": round(float(precio_hoy), 2),
        }

        if estado_key:
            alertas.append({
                "Ticker": ticker, "Sector": sector,
                "Estado": ESTADOS.get(estado_key, estado_key),
                "Score": f"{score_mostrado}/7",
                "Score_num": score_mostrado,
                "Señales": señales,
                "VCP": vcp_resultado,
                "RSI": round(rsi_hoy, 1), "Vol_rel": round(vol_rel_hoy, 2),
                "SMA21": round(sma_cortas[21].iloc[-1], 2) if not pd.isna(sma_cortas[21].iloc[-1]) else None,
            })

    return pd.DataFrame(alertas), historial
