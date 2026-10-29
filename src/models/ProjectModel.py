from .BaseDataModel import BaseDataModel
from .schemes import Project
from .enums.DataBase_Enums import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client:object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]


    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name= index["name"],
                    unique=index["unique"]
                )

    async def create_project(self,project:Project):
        #. The await allows the function to suspend while waiting for that operation to complete, so it can use the result afterward.
        result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_none=True)) #instead of .dic()
        #You're querying the actual database, whose document field is named _id.You are not accessing a Pydantic model attribute here.
        project._id = result.inserted_id 
        return project

    async def get_project_or_create_one(self,project_id:str):
        record = await self.collection.find_one({
            "project_id":project_id
        })
        if record is None :
            project = Project(project_id=project_id)
            project = await self.create_project(project=project)
            return project
        return Project(**record) #The caller receives a Project object, created from the dictionary

    
    async def get_all_projects(self,page:int=1 , page_size:int=10):
        #total number of projects
        total_documents = await self.collection.count_documents({})

        # calculate total number of pages
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1
        #Find my projects, skip the ones before the page I want, and return at most 10 projects
        cursor = self.collection.find().skip((page-1) * page_size).limit(page_size)
        #find() typically returns a cursor, not a Python list containing all the documents.
        projects=[]
        async for doc in cursor:
            projects.append(Project(**doc))
        return projects,total_pages
