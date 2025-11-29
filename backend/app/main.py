from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
from app.core.database import engine, Base
from app.api import products, chat, scraper


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
    except Exception as e:
        print(f"Note: pgvector extension might already exist: {e}")
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Mane API",
    description="Hair care e-commerce backend with RAG-powered product recommendations",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(scraper.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Mane API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}
