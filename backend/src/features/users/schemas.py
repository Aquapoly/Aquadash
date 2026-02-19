
from pydantic import BaseModel

# Authentification stuff
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str


class UserInDB(User):
    pw_hash: str
    pw_salt: str
    id: int
