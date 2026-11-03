from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from routes import base, data
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    # ---------------- Startup ----------------
    # 1. Database
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    # 2. Provider factory
    llm_provider_factory = LLMProviderFactory(settings)

    # 3. Generation client
    app.generation_client = llm_provider_factory.create(
        provider=settings.GENERATION_BACKEND
    )
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # 4. Embedding client
    app.embedding_client = llm_provider_factory.create(
        provider=settings.EMBEDDING_BACKEND
    )
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE,
    )

    # Application serves requests while yielded
    yield

    # ---------------- Shutdown ----------------
    app.mongo_conn.close()


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)