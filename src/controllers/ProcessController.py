from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from models import ProcessingEnum
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from dataclasses import dataclass
import logging
logger = logging.getLogger('uvicorn.error')

@dataclass
class Document:
    page_content: str
    metadata: dict

class ProcessController(BaseController):
    def __init__(self, project_id:str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().project_path(project_id)
        self.logger = logger


    def get_file_extension(self , file_id : str):
        return os.path.splitext(file_id)[-1]

    def get_file_loder(self , file_id :str):
        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(
            self.project_path , 
            file_id
        )

        if not os.path.exists(file_path):
            return None
        
        if file_ext == ProcessingEnum.TXT.value :
            return TextLoader(file_path , encoding = "utf-8")
        if file_ext == ProcessingEnum.PDF.value :
            return PyMuPDFLoader(file_path)
        return None
    def get_file_content(self , file_id:str):
        loader = self.get_file_loder(file_id=file_id)

        if loader:
            return loader.load()
        return None

    def process_file_content(
        self,
        file_id: str,
        file_content: list,
        chunk_size: int = 100,
        overlap_size: int = 20
    ):
        if not file_content:
            self.logger.warning(f"No content found for file: {file_id}")
            return []

        file_content_texts = [
            rec.page_content
            for rec in file_content
            if rec.page_content and rec.page_content.strip()
        ]

        file_content_metadata = [
            rec.metadata
            for rec in file_content
            if rec.page_content and rec.page_content.strip()
        ]

        if not file_content_texts:
            self.logger.warning(f"File contains no readable text: {file_id}")
            return []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )

        chunks = text_splitter.create_documents(
            file_content_texts,
            metadatas=file_content_metadata
        )

        self.logger.info(f"Successfully generated {len(chunks)} chunks")

        return chunks




    def process_simpler_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int, splitter_tag: str="\n"):
        
        full_text = " ".join(texts)

        # split by splitter_tag
        lines = [ doc.strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) > 1 ]

        chunks = []
        current_chunk = ""

        for line in lines:
            current_chunk += line + splitter_tag
            if len(current_chunk) >= chunk_size:
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata={}
                ))

                current_chunk = ""

        if len(current_chunk) >= 0:
            chunks.append(Document(
                page_content=current_chunk.strip(),
                metadata={}
            ))

        return chunks
        

