from abc import ABC, abstractmethod

class LLMInterface(ABC):

    @abstractmethod
    def set_generation_model(self, model_id: str):
        """
        Selects/configures the generation model , return nothing
        """
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int):
        """
        Selects/configures the embedding model , return nothing
        """
        pass

    @abstractmethod
    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None):
        """
        Sends a prompt to the generation model, and returns the generated text as a string.
        """
        pass

    @abstractmethod
    def embed_text(self, text: str, document_type: str = None):
        """
        Converts text into a numerical vector"""
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        """
        Formats a prompt with its role
        """
        pass