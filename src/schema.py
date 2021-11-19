from pydantic import BaseModel

class UserDetails(BaseModel):
    username: str
    password: str