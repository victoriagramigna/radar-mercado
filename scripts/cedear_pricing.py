"""
Señal de "CEDEAR caro/barato": compara el precio real del CEDEAR en pesos
(BYMA, vía data912.com) contra su valor teórico (precio de la acción real
en USD x CCL / ratio de conversión).

Esto NO es una señal de "buena empresa" -- es una señal de "buen momento de
ejecución hoy en pesos", útil sobre todo en feriados de EEUU (el precio en
USD queda congelado, pero el CEDEAR y el CCL siguen moviéndose en Argentina).

data912.com es una API pública/educativa, sin auth, con caché de ~2hs.
Si falla o cambia de formato, esta función se degrada sin romper el resto
de la corrida (mismo patrón que macro_local.py).
"""
import logging
import requests

from config import RATIOS_CEDEAR, BRECHA_CEDEAR_ALERTA_PCT

log = logging.getLogger("radar.cedear_pricing")

BASE = "https://data912.com"
TIMEOUT = 10

# Nombres de campo candidatos -- no pudimos confirmar el schema exacto de
# data912 sin poder probarlo en vivo desde este entorno de desarrollo, así
# que probamos varias claves típicas. Si ninguna aparece, se loguea la
# respuesta cruda para poder ajustar esto con el primer dato real.
CAMPOS_PRECIO_CANDIDATOS = ["c", "close", "last", "px", "precio", "ultimo"]
CAMPOS_SYMBOL_CANDIDATOS = ["symbol", "ticker", "simbolo", "ticker_symbol"]


def _extraer_campo(item: dict, candidatos: list, default=None):
    for campo in candidatos:
        if campo in item and item[campo] not in (None, ""):
            return item[campo]
    return default


def traer_ccl():
    """Devuelve el valor del CCL (venta) o None si falla."""
    try:
        resp = requests.get(f"{BASE}/live/ccl", timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        # La respuesta puede ser un dict único o una lista con una entrada
        item = data[0] if isinstance(data, list) else data
        valor = _extraer_campo(item, ["venta", "ask", "sell"] + CAMPOS_PRECIO_CANDIDATOS)
        if valor is None:
            log.warning(f"CCL: no se encontró un campo de precio reconocible. Respuesta cruda: {item}")
            return None
        return float(valor)
    except Exception as e:
        log.warning(f"No se pudo traer CCL: {e}")
        return None


def traer_precios_cedears(tickers: list):
    """Devuelve {ticker: precio_ars} para los tickers pedidos, o {} si falla todo."""
    try:
        resp = requests.get(f"{BASE}/live/arg_cedears", timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log.warning(f"No se pudo traer el panel de CEDEARs: {e}")
        return {}

    precios = {}
    tickers_set = set(tickers)
    for item in data:
        symbol = _extraer_campo(item, CAMPOS_SYMBOL_CANDIDATOS)
        if symbol is None:
            continue
        symbol = str(symbol).upper().replace(".BA", "").strip()
        if symbol not in tickers_set:
            continue
        precio = _extraer_campo(item, CAMPOS_PRECIO_CANDIDATOS)
        if precio is not None:
            precios[symbol] = float(precio)

    faltantes = tickers_set - set(precios.keys())
    if faltantes:
        log.warning(f"No se encontró precio de CEDEAR para: {sorted(faltantes)} "
                     f"(puede ser un problema de nombre de campo -- revisar schema real)")
    return precios


def calcular_brechas_cedear(precios_usd: dict):
    """
    precios_usd: {ticker: precio_actual_en_usd} (ya lo tenemos calculado en rs_score.py)
    Devuelve una lista de dicts, uno por CEDEAR con ratio conocido, con el
    precio real, el teórico, y el % de brecha entre ambos.
    """
    ccl = traer_ccl()
    if ccl is None:
        return {"ccl": None, "sin_datos": True, "cedears": []}

    tickers_con_ratio = [t for t in RATIOS_CEDEAR if t in precios_usd]
    precios_ars = traer_precios_cedears(tickers_con_ratio)

    resultados = []
    for ticker in tickers_con_ratio:
        precio_usd = precios_usd[ticker]
        ratio = RATIOS_CEDEAR[ticker]
        precio_ars_real = precios_ars.get(ticker)

        teorico = round((precio_usd * ccl) / ratio, 2)

        if precio_ars_real is None:
            resultados.append({
                "Ticker": ticker, "sin_datos": True,
                "Precio_teorico_ARS": teorico,
            })
            continue

        brecha_pct = round((precio_ars_real / teorico - 1) * 100, 2)
        distorsion = abs(brecha_pct) >= BRECHA_CEDEAR_ALERTA_PCT

        resultados.append({
            "Ticker": ticker,
            "sin_datos": False,
            "Precio_real_ARS": precio_ars_real,
            "Precio_teorico_ARS": teorico,
            "Brecha_%": brecha_pct,
            "Estado": ("Caro respecto al teórico" if brecha_pct > 0 else "Barato respecto al teórico"),
            "Distorsion_relevante": distorsion,
        })

    return {"ccl": ccl, "sin_datos": False, "cedears": resultados}
