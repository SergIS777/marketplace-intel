from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, store, reviews, trainer

app = FastAPI(title="Marketplace Intel API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(store.router, prefix="/api/v1", tags=["store"])
app.include_router(reviews.router, prefix="/api/v1", tags=["reviews"])
app.include_router(trainer.router, prefix="/api/v1", tags=["trainer"])

@app.get("/")
async def root():
    return {"message": "Marketplace Intel API", "version": "0.1.0", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "ok"}
