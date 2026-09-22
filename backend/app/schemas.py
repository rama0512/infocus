import re 
from pydantic import BaseModel, EmailStr,validator
from typing import Optional,Dict, Any
from datetime import datetime

class usercreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    @validator('username')
    def username_analysis(cls,v):
        clean_v = v.strip()
        if len(clean_v) < 3:
            raise ValueError('Username must be at least 3 characters long and no spaces')
        if not re.match(r"^[a-zA-Z0-9_]+$", clean_v):
            raise ValueError('Username must contain only lowercase letters, numbers, and underscores')
        return clean_v

class userresponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class userlogin(BaseModel):
    email: EmailStr
    password: str


class userloginresponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class webcam_result_create(BaseModel):
    s3_path: str
    captured_at_ms: int
    coordinates: Dict[str, Any]
