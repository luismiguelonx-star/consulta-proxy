# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 09:08:30 2026

@author: luis chavarro
"""

from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/consulta/{variable}")
def consulta(variable: str, fechaInicio: str, fechaFin: str):
    url = f"https://serviciospub.xm.com.co/api/variables/{variable}"
    params = {
        "fechaInicio": fechaInicio,
        "fechaFin": fechaFin
    }
    r = requests.get(url, params=params)
    return r.json()
