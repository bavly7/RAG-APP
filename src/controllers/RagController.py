from .BaseController import BaseController
from models.schemes import Project,ChunkData
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List
import json


class RagController(BaseController):
    def __init__(self,vectordb_client,generation_client,embedding_client,template_parser):
#need Vecotor DB --> LLM form emb --> Generation Client
        super().__init__()
        self.vectordb_client=vectordb_client
        self.generation_client=generation_client
        self.embedding_client=embedding_client
        self.template_parser=template_parser

    def create_collection_name(self,project_id:str):
        return f"collection_{project_id}".strip()

    def reset_vectordb_collection(self,project:Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)


    def get_vectordb_collection_info(self,project:Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info=self.vectordb_client.get_collection_info(collection_name=collection_name)

        # return collection_info
        return json.loads(
            json.dumps(collection_info,default=lambda x:x.__dict__)
        )

    def index_into_vector_db(self,project:Project,chunks:List[ChunkData], chunks_ids :List[int],do_reset:bool =False ):
        collection_name = self.create_collection_name(project_id=project.project_id)

        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]
        vectors = [
            self.embedding_client.embed_text(text=text , document_type = DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]


        _ = self.vectordb_client.create_collection(
            collection_name= collection_name,
            embedding_size = self.embedding_client.embedding_size,
            do_reset=do_reset,
        )


        insert_result = self.vectordb_client.insert_many(
                collection_name=collection_name,
                texts=texts,
                vectors=vectors,
                metadata=metadata,
                record_ids=chunks_ids
                    )

        ## thats for logging

        # print("Chunks received:", len(chunks))
        # print("Texts extracted:", len(texts))
        # print("Metadata extracted:", len(metadata))
        # print("Embeddings generated:", len(vectors))
        # print("First embedding length:", len(vectors[0]) if vectors else None)
        # print("Chunk IDs:", chunks_ids)
        # print("Insertion result:", insert_result)
        # print(
        #     "Stored points:",
        #     self.vectordb_client.client.count(
        #         collection_name=collection_name,
        #         exact=True
        #     ).count
        # )

        if not insert_result:
            return False

        return True



    def search_vector_db_collection(self, project: Project, text: str, limit: int = 5):

        collection_name = self.create_collection_name(
            project_id=project.project_id
        )

        # print("Collection:", collection_name)

        vector = self.embedding_client.embed_text(
            text=text,
            document_type=DocumentTypeEnum.QUERY.value
        )

        # print("Vector exists:", vector is not None)
        # print("Vector length:", len(vector) if vector is not None else None)

        if not vector or len(vector) == 0:
            print("ERROR: Embedding generation failed")
            return False

        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        # print("Search results count:", len(results))

        if not results:
            print("ERROR: No matching records found")
            return False

        return results

    def rag_answer_question(self, project: Project, query: str, limit: int = 5):

        answer,full_prompt,chat_history = None,None,None

        retrieved_docs = self.search_vector_db_collection(
            project=project,
            text=query,
            limit= limit
        )
        if not retrieved_docs or len(retrieved_docs) ==0:
            return answer,full_prompt,chat_history

        system_prompt = self.template_parser.get("prompts","system_prompt")

        # document_prompts = []
        # for i , doc in enumerate(retrieved_docs):
        #     document_prompts.append(
        #         self.template_parser.get("prompts","document_prompt",{
        #             "doc_num" : i + 1,
        #             "chunk_text" : doc.text
        #         })
        #     )

        document_prompts = "\n".join([
            self.template_parser.get("prompts","document_prompt",
                {
                    "doc_num" : i + 1,
                    "chunk_text" : doc.text
                }
            )
            for i , doc in enumerate(retrieved_docs)
        ])

        footer_prompt = self.template_parser.get("prompts","footer_prompt")

        chat_history = [
            self.generation_client.construct_prompt(
                prompt = system_prompt,
                role = self.generation_client.enums.SYSTEM.value ,
            )
        ]

        full_prompt = "\n\n".join([document_prompts,footer_prompt])

        answer = self.generation_client.generate_text(
            prompt = full_prompt,
            chat_history=chat_history
        )

        return answer , full_prompt,chat_history







