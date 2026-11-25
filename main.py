import math
import os

from fastapi import FastAPI, HTTPException
from pydantic import FiniteFloat

APP_VERSION = os.getenv("APP_VERSION", "local")
app = FastAPI(title="API Calculator", version=APP_VERSION)


def result(value: float) -> dict[str, float]:
    if not math.isfinite(value):
        raise HTTPException(status_code=400, detail="Result is not finite")
    return {"result": value}


@app.get("/")
def home():
    return {"message": "API Calculator is running"}


@app.get("/add")
def add(a: FiniteFloat, b: FiniteFloat):
    return result(a + b)


@app.get("/subtract")
def subtract(a: FiniteFloat, b: FiniteFloat):
    return result(a - b)


@app.get("/multiply")
def multiply(a: FiniteFloat, b: FiniteFloat):
    return result(a * b)


@app.get("/divide")
def divide(a: FiniteFloat, b: FiniteFloat):
    if b == 0:
        raise HTTPException(status_code=400, detail="Division by zero is not allowed")
    return result(a / b)


@app.get("/power")
def power(a: FiniteFloat, b: FiniteFloat):
    try:
        value = math.pow(a, b)
    except (ValueError, OverflowError):
        raise HTTPException(status_code=400, detail="Power is outside the real finite range") from None
    return result(value)


@app.get("/mod")
def mod(a: FiniteFloat, b: FiniteFloat):
    if b == 0:
        raise HTTPException(status_code=400, detail="Division by zero is not allowed")
    return result(a % b)


@app.get("/version")
def version():
    return {"version": APP_VERSION}
