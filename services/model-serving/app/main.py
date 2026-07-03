"""FastAPI serving endpoint for the demonstration splice-junction classifier.

Loads a bundled scikit-learn pipeline (see app/model_loader.py) once at
startup and serves predictions from it -- no live database, cache, or
MLflow dependency at request time. See the service README for the
"demonstration stand-in, not production-grade" scope note: this predicts
a classic UCI benchmark's EI/IE/N labels, not clinical or genome-scale
splice-site calls.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.features import encode_sequence
from app.model_loader import ModelBundle, load_model_bundle
from app.schemas import HealthResponse, ModelInfoResponse, PredictRequest, PredictResponse

_state: dict[str, ModelBundle] = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    _state["bundle"] = load_model_bundle()
    yield
    _state.clear()


app = FastAPI(
    title="GenomeRSE model-serving",
    description=(
        "Demonstration splice-junction classifier serving endpoint. "
        "Not a production-grade splice-site predictor -- see README."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


def _get_bundle() -> ModelBundle:
    bundle = _state.get("bundle")
    if bundle is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    return bundle


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/model-info", response_model=ModelInfoResponse)
async def model_info() -> ModelInfoResponse:
    metadata = _get_bundle().metadata
    return ModelInfoResponse(**metadata.__dict__)


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    bundle = _get_bundle()
    features = encode_sequence(request.sequence).reshape(1, -1)
    predicted_class = bundle.model.predict(features)[0]
    probability_values = bundle.model.predict_proba(features)[0]
    classes = bundle.model.named_steps["classifier"].classes_
    probabilities = {
        class_name: float(probability)
        for class_name, probability in zip(classes, probability_values, strict=True)
    }
    return PredictResponse(predicted_class=predicted_class, probabilities=probabilities)
