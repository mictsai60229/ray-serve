from pydantic import BaseModel

class GreetingResponse(BaseModel):
    text: str = 'Hello world'