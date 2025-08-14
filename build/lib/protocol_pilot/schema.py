from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError, model_validator

class Reagent(BaseModel):
    name: str
    amount: Optional[float] = Field(default=None, description="Numeric amount if known")
    unit: Optional[str] = Field(default=None, description="Unit for amount, e.g., µL, mg, mM")
    vendor: Optional[str] = None
    catalog_number: Optional[str] = None

class Step(BaseModel):
    number: int
    description: str
    duration_minutes: Optional[float] = None
    temperature_c: Optional[float] = None
    hazards: List[str] = []

class Protocol(BaseModel):
    title: str
    sources: List[str]
    equipment: List[str] = []
    reagents: List[Reagent] = []
    steps: List[Step]
    safety_notes: List[str] = []
    ruo_disclaimer: str

    @model_validator(mode="after")
    def check_steps_sequential(self):
        nums = [s.number for s in self.steps]
        if nums != list(range(1, len(nums) + 1)):
            raise ValueError("Steps must be sequential starting at 1")
        return self

def validate_protocol(proto: Protocol) -> None:
    """Raises ValidationError if invalid."""
    if not proto.ruo_disclaimer.lower().startswith("research use only"):
        raise ValidationError([{"loc":("ruo_disclaimer",), "msg":"Missing RUO disclaimer"}], Protocol)
