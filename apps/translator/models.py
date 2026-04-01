from pydantic import BaseModel

class TranslatorRequest(BaseModel):
    language: str = 'en'
    text: str

class TranslatorResponse(BaseModel):
    text: str