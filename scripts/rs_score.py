"""
Cálculo de RS Score (Relative Strength) vs benchmark, agrupable por sector.
Lógica validada previamente con datos simulados -- ver conversación de diseño.
"""
import pandas as pd


def calcular_rs_score(precios: dict, tickers_sector: dict, benchmark: str):
    resultados = []
    if benchmark not in precios:
        raise ValueError(f"Benchmark '{benchmark}' no disponible en los datos traídos")
    bench = precios[benchmark].dropna()

    def rendimiento(serie, dias):
        if len(serie) <= dias:
            return None
        return (serie.iloc[-1] / serie.iloc[-dias]) - 1

    for ticker, sector in tickers_sector.items():
        if ticker not in precios:
            continue  # ya quedó logueado como fallido en datos.py
        close = precios[ticker].dropna()
        if len(close) < 126:
            continue

        precio_actual = close.iloc[-1]
        ret_1m, ret_3m, ret_6m = rendimiento(close, 21), rendimiento(close, 63), rendimiento(close, 126)
        b_1m, b_3m, b_6m = rendimiento(bench, 21), rendimiento(bench, 63), rendimiento(bench, 126)
        if None in (ret_1m, ret_3m, ret_6m, b_1m, b_3m, b_6m):
            continue

        rs_raw = ((ret_1m - b_1m) * 0.4) + ((ret_3m - b_3m) * 0.3) + ((ret_6m - b_6m) * 0.3)

        sma50 = close.rolling(50).mean().iloc[-1]
        max_52w = close.max()

        resultados.append({
            "Ticker": ticker, "Sector": sector, "Precio": round(precio_actual, 2),
            "RS_raw": rs_raw,
            "Ret_1m_%": round(ret_1m * 100, 1), "Ret_3m_%": round(ret_3m * 100, 1),
            "Ret_6m_%": round(ret_6m * 100, 1),
            "Sobre_SMA50": bool(precio_actual > sma50),
            "Dist_Max52w_%": round((precio_actual / max_52w - 1) * 100, 1),
        })

    df = pd.DataFrame(resultados)
    if df.empty:
        return df
    df["RS_Score"] = (df["RS_raw"].rank(pct=True) * 100).round(1)
    return df.drop(columns=["RS_raw"]).sort_values("RS_Score", ascending=False).reset_index(drop=True)
