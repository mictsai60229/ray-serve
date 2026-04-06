from pydantic import BaseModel

class ChainRequest(BaseModel):
    input: int

    
class ChainResponse(BaseModel):
    output: int