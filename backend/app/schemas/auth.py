from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3)
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str