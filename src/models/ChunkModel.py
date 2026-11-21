#UPDATE MONGO to POSTGRESQL
from .BaseDataModel import BaseDataModel
from .schemes import ChunkData
from .enums.DataBase_Enums import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne
from sqlalchemy import select , delete

class ChunkModel (BaseDataModel):
    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        self.db_client = self.db_client

    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client)
        # await instance.init_collection()
        return instance

    # async def init_collection(self):
    #     all_collections = await self.db_client.list_collection_names()
    #     if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collections:
    #         self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
    #         indexes = ChunkData.get_indexes()
    #         for index in indexes:
    #             await self.collection.create_index(
    #                 index["key"],
    #                 name= index["name"],
    #                 unique=index["unique"]
    #             )



    async def create_chunk(self ,chunk:ChunkData):
        async with self.db_client() as session:
            async with session.begin():
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
        return chunk

    async def get_chunk(self ,chunk_id:str):
        async with self.db_client() as session:
            result = await session.execute(select(ChunkData).where(ChunkData.chunk_id == chunk_id))
            chunk = result.scalar_one_or_none()
        return chunk

    async def insert_many_chunks(self,chunks:list,batch_size:int=100):
        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i:i+batch_size]
                    session.add_all(batch)
            await session.commit()
        return len(chunks)
    async def delete_chunks_by_project_id(self,project_id:ObjectId):
        async with self.db_client() as session:
            stmt = delete(ChunkData).where(ChunkData.chunk_project_id == project_id)
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount

    async def get_poject_chunks(self, project_id: ObjectId, page_no: int=1, page_size: int=50):
        async with self.db_client() as session:
            stmt = select(ChunkData).where(ChunkData.chunk_project_id == project_id).offset((page_no - 1) * page_size).limit(page_size)
            result = await session.execute(stmt)
            records = result.scalars().all()
        return records