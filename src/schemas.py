from pydantic import BaseModel as Base
from pydantic import Field, ConfigDict

class BaseModel(Base):
    model_config = ConfigDict(str_strip_whitespace=True)

class SRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=8, max_length=128)

class SLogin(SRegister):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)

class SNewScreenshot(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    url: str = Field(..., min_length=1, max_length=128)
    screenshot_name: str | None = Field(None, min_length=2, max_length=50)

class SScreenshots(BaseModel):
    screenshot_ids: list[int] = Field(..., min_length=1)

class SAccountSettings(BaseModel):
    new_username: str | None = Field(None, min_length=2, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)

class SNewPassword(BaseModel):
    old_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_new_password: str = Field(..., min_length=1, max_length=128)

class SDeleteAccount(BaseModel):
    password: str = Field(..., min_length=1, max_length=128)

class SEditScreenshots(BaseModel):
    class Detail(BaseModel):
        is_deleted: bool
        name: str
        public: bool
    to_change: dict[int, Detail] = Field(..., min_length=1, max_length=128)
