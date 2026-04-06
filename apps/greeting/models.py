from pydantic import BaseModel

class GreetingRequest(BaseModel):
    lang: str = 'zh-tw'

class GreetingResponse(BaseModel):
    text: str = 'Hello world'