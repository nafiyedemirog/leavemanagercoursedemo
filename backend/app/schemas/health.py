from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health status only — no version, environment or host details (spec 0001, AC-2)."""

    status: Literal["ok"]
