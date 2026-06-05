from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pandas as pd
import requests

app = FastAPI()

# CORS para permitir acceso desde Streamlit y Cloudflare Worker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
#   FUNCIÓN QUE REPLICA EXACTAMENTE A consulta_xm()
# ============================================================
def obtener_datos(variable, tipo, fecha_inicio, fecha_fin):

    url = f"https://serviciospub.xm.com.co/api/variables/{variable}"

    params = {
        "fechaInicio": fecha_inicio,
        "fechaFin": fecha_fin
    }

    r = requests.get(url, params=params)

    if r.status_code != 200:
        return {"error": f"Error consultando datos: {r.status_code}"}

    data = r.json()

    # Convertir a DataFrame conservando TODAS las columnas originales
    df = pd.DataFrame(data["valores"])

    # Convertir tipos
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    if "valor" in df.columns:
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    # Mantener tu estructura original
    df["tipo"] = tipo

    return df


# ============================================================
#   ENDPOINT PRINCIPAL
# ============================================================
@app.get("/consulta/{variable}/{tipo}")
def consulta(variable: str, tipo: str, fechaInicio: str, fechaFin: str):

    # Validar fechas
    try:
        datetime.strptime(fechaInicio, "%Y-%m-%d")
        datetime.strptime(fechaFin, "%Y-%m-%d")
    except:
        return {"error": "Formato de fecha inválido. Use YYYY-MM-DD"}

    df = obtener_datos(variable, tipo, fechaInicio, fechaFin)

    if isinstance(df, dict):  # error
        return df

    return df.to_dict(orient="records")
