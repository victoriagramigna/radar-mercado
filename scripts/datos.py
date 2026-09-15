"""
Traída de datos de precios/volumen. Si un ticker falla, se loguea y se sigue
con el resto -- un ticker roto no debe tumbar la corrida completa.
"""
import logging
import yfinance as yf

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("radar.datos")


def traer_datos(tickers: dict, benchmark: str, periodo: str = "1y"):
    """
    tickers: dict {ticker: sector}
    Devuelve (precios, volumenes, tickers_fallidos)
    precios/volumenes: dict {ticker: pd.Series}
    tickers_fallidos: lista de tickers que no se pudieron traer, con el motivo
    """
    simbolos = list(tickers.keys()) + [benchmark]
    precios, volumenes = {}, {}
    fallidos = []

    log.info(f"Descargando {len(simbolos)} símbolos (período={periodo})...")

    for simbolo in simbolos:
        try:
            hist = yf.Ticker(simbolo).history(period=periodo, auto_adjust=True)
            if hist.empty or len(hist) < 200:
                raise ValueError(f"datos insuficientes ({len(hist)} filas, se necesitan >=200)")
            precios[simbolo] = hist["Close"]
            volumenes[simbolo] = hist["Volume"]
        except Exception as e:
            log.warning(f"  ⚠ {simbolo}: falló ({e}) -- se omite de esta corrida")
            fallidos.append({"ticker": simbolo, "motivo": str(e)})

    log.info(f"OK: {len(precios)} símbolos. Fallidos: {len(fallidos)}")
    return precios, volumenes, fallidos


if __name__ == "__main__":
    # Prueba rápida (requiere red habilitada al host de Yahoo Finance --
    # en este sandbox de desarrollo está bloqueado a propósito; correr
    # este archivo directamente en GitHub Actions o en tu máquina local).
    from config import TICKERS, BENCHMARK
    precios, volumenes, fallidos = traer_datos(TICKERS, BENCHMARK)
    print(f"Precios OK: {list(precios.keys())}")
    print(f"Fallidos: {fallidos}")
