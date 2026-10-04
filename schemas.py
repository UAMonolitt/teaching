from pydantic import BaseModel, Field

class SRegisterLogin(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)