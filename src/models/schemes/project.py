from pydantic import Field , BaseModel , field_validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    #tells Pydantic that this field corresponds to MongoDB's field named
    id : Optional[ObjectId]= Field(None, alias="_id")#MongoDB uses _id as the default name for a document's ID
    project_id: str = Field(..., min_length=1)

    @field_validator('project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        
        return value

    class Config: #let pydantic know what is ObjectId 
        arbitrary_types_allowed = True