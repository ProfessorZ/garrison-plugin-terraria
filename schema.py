from pydantic import BaseModel, Field
from typing import Optional


class TerrariaConnectionConfig(BaseModel):
    host: str = Field(..., description="TShock server hostname or IP")
    port: int = Field(7878, description="TShock REST API port (default: 7878)")
    password: str = Field(..., description="TShock REST API password")


class TerrariaPlayerInfo(BaseModel):
    name: str
    ip: Optional[str] = None
    team: Optional[int] = None
    difficulty: Optional[str] = None
