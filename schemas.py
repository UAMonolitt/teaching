from pydantic import BaseModel, Field, ConfigDict

class SRegister(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
    model_config = ConfigDict(str_strip_whitespace=True)

class SLogin(SRegister):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

class SScreenshot(BaseModel):
    screenshot_name: str | None = Field(None, min_length=1, max_length=50)
    delete_after: float | None = Field(None, ge=60, le=15552000)
    url: str = Field(..., max_length=128)

    model_config = ConfigDict(str_strip_whitespace=True)