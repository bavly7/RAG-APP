import logging

from groq import Groq

from llm.LLMInterface import LLMInterface
from llm.LLMEnums import GroqAIEnums


class GroqAIProvider(LLMInterface):

    def __init__(
        self,
        api_key: str,
        default_input_max_characters: int = 1000,
        default_generation_max_output_tokens: int = 1000,
        default_generation_temperature: float = 0.1,
        top_p: float = 1.0,
        stop: list = None,
        streaming: bool = False,
    ):
        self.api_key = api_key

        # Input-processing limit (characters), NOT generation tokens
        self.default_input_max_characters = default_input_max_characters

        # Generation defaults
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.top_p = top_p
        self.stop = stop
        self.streaming = streaming

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = Groq(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------ #
    # Model setters
    # ------------------------------------------------------------------ #
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    # ------------------------------------------------------------------ #
    # Text processing
    # ------------------------------------------------------------------ #
    def process_text(self, text: str):
        # Character limit for INPUT, not output tokens
        return text.strip()[: self.default_input_max_characters]

    # ------------------------------------------------------------------ #
    # Generation
    # ------------------------------------------------------------------ #
    def generate_text(
        self,
        prompt: str,
        chat_history: list = None,
        max_output_tokens: int = None,
        temperature: float = None,
        top_p: float = None,
        stop: list = None,
        streaming: bool = None,
    ):
        if not self.client:
            self.logger.error("GroqAI client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for GroqAI was not set")
            return None

        # Use `is None` so 0.0 / [] / False are preserved
        max_output_tokens = (
            max_output_tokens
            if max_output_tokens is not None
            else self.default_generation_max_output_tokens
        )
        temperature = (
            temperature
            if temperature is not None
            else self.default_generation_temperature
        )
        top_p = top_p if top_p is not None else self.top_p
        stop = stop if stop is not None else self.stop
        streaming = streaming if streaming is not None else self.streaming

        # Initialise history and append the current user prompt
        if chat_history is None:
            chat_history = []

        chat_history.append(
            self.construct_prompt(prompt=prompt, role=GroqAIEnums.USER.value)
        )

        # NOTE: Groq Chat Completions API (not OpenAI Responses API)
        try:
            response = self.client.chat.completions.create(
                model=self.generation_model_id,
                messages=chat_history,
                max_completion_tokens=max_output_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop,
                stream=streaming,
            )
        except Exception as e:
            self.logger.error(f"GroqAI generation error: {e}")
            return None

        if not response:
            self.logger.error("No response received from GroqAI")
            return None

        # Streaming returns an iterator of chunks
        if streaming:
            return response

        # Non-streaming response structure
        if not response.choices or len(response.choices) == 0:
            self.logger.error("GroqAI returned no choices")
            return None

        return response.choices[0].message.content

    # ------------------------------------------------------------------ #
    # Embeddings — Groq does not provide embeddings
    # ------------------------------------------------------------------ #
    def embed_text(self, text: str, document_type: str = None):
        raise NotImplementedError(
            "GroqAIProvider does not support embeddings in this implementation. "
            "Use OpenAI or Cohere for embedding."
        )

    # ------------------------------------------------------------------ #
    # Prompt construction
    # ------------------------------------------------------------------ #
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt),
        }