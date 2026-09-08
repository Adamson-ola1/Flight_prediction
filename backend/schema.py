"""
schema.py — request/response models for the FastAPI backend.
"""
from pydantic import BaseModel, ConfigDict, Field


class FlightRequest(BaseModel):
    year: int = Field(..., ge=2013, le=2035, examples=[2013])
    month: int = Field(..., ge=1, le=12, examples=[7])
    day: int = Field(..., ge=1, le=31, examples=[19])
    hour: int = Field(..., ge=0, le=23, examples=[8])
    minute: int = Field(..., ge=0, le=59, examples=[30])
    carrier: str = Field(..., min_length=2, max_length=2, examples=["DL"])
    origin: str = Field(..., examples=["JFK"], description="One of JFK, LGA, EWR")
    dest: str = Field(..., examples=["LAX"], description="3-letter destination airport code")
    distance: float = Field(..., gt=0, le=3000, examples=[2475])


class FlightPredictionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    predicted_price: float
    currency: str = "USD"
    model_used: str


class BatchFlightRequest(BaseModel):
    flights: list[FlightRequest]


class BatchFlightPredictionResponse(BaseModel):
    predictions: list[FlightPredictionResponse]


class MetricsResponse(BaseModel):
    best_model: str
    leaderboard: dict
    n_test_rows: int


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool
