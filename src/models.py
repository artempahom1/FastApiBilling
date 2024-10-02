from pydantic import BaseModel



class SetBody(BaseModel):
    domain: str
    timeout_value: int
