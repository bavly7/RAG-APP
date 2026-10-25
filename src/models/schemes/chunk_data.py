from pydantic import Field , BaseModel , field_validator
from typing import Optional
from bson.objectid import ObjectId

class ChunkData(BaseModel):
    _id : Optional[ObjectId]#MongoDB uses _id as the default name for a document's ID
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata :dict
    chunk_order : int = Field(...,gt=0) #gt == greater than 
    chunk_project_id : ObjectId


    @field_validator('project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        
        return value

    class Config: #let pydantic know what is ObjectId 
        arbitrary_types_allowed = True