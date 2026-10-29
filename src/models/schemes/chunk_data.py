from pydantic import Field , BaseModel , field_validator
from typing import Optional
from bson.objectid import ObjectId

class ChunkData(BaseModel):
    #tells Pydantic that this field corresponds to MongoDB's field named
    id : Optional[ObjectId]=Field(None,alias="_id")#MongoDB uses _id as the default name for a document's ID
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata :dict
    chunk_order : int = Field(...,gt=0) #gt == greater than 
    chunk_project_id : ObjectId

    class Config: #let pydantic know what is ObjectId 
        arbitrary_types_allowed = True



    @classmethod
    def get_indexes(cls):
        return [
            {
                "key" : [
                    ("chunk_project_id",1)
                ],
                "name":"chunk_project_id_index_1",
                "unique":False
            }
        ]