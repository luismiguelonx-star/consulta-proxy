from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pandas as pd
import requests

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
#   FUNCIÓN ROBUSTA PARA CONSULTAR XM
# ============================================================
def obtener_datos(variable, tipo, fecha_inicio, fecha_fin):

    url = f"https://serviciospub.xm.com.co/api/variables/{variable}"

    params = {
        "fechaInicio": fecha_inicio,
        "fechaFin": fecha_fin
    }

    try:
        r = requests.get(url, params=params, timeout=20)
    except Exception as e:
        return {"error": f"Error de conexión: {str(e)}"}

    # Si XM responde con error HTTP
    if r.status_code != 200:
        return {"error": f"XM devolvió código {r.status_code}"}

    # Intentar leer JSON
    try:
        data = r.json()
    except:
        return {"error": "XM devolvió un formato no JSON"}

    # Validar que existan datos
    if "valores" not in data or len(data["valores"]) == 0:
        return {"error": "XM no devolvió datos para esta consulta"}

    # Convertir a DataFrame
    df = pd.DataFrame(data["valores"])

    # Convertir tipos
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    if "valor" in df.columns:
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    # Agregar tipo
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

    # Si hubo error, devolverlo
    if isinstance(df, dict):
        return df

    return df.to_dict(orient="records")
