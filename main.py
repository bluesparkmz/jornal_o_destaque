from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from controllers.bootstrap_controller import create_initial_admin
from database import SessionLocal
from routers import admin, articles, auth, engagement, media, newspapers, taxonomy


cfg = settings()
cfg.upload_dir.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=cfg.app_name,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.mount("/uploads", StaticFiles(directory=cfg.upload_dir), name="uploads")

app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(taxonomy.router)
app.include_router(engagement.router)
app.include_router(newspapers.router)
app.include_router(media.router)
app.include_router(admin.router)


@app.on_event("startup")
def bootstrap_admin() -> None:
    session = SessionLocal()
    try:
        create_initial_admin(session)
    finally:
        session.close()


@app.get("/health", tags=["Sistema"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": cfg.app_name}
