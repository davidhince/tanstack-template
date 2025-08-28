from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os


def ensure_data_dir() -> None:
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)


ensure_data_dir()

app = FastAPI(title="AI Personal Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
from .routes.chat import router as chat_router  # noqa: E402
from .routes.todos import router as todos_router  # noqa: E402
from .routes.reminders import router as reminders_router  # noqa: E402
from .services.reminders import start_scheduler, shutdown_scheduler  # noqa: E402


@app.on_event("startup")
async def on_startup() -> None:
    await start_scheduler()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await shutdown_scheduler()


app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(todos_router, prefix="/api", tags=["todos"])
app.include_router(reminders_router, prefix="/api", tags=["reminders"])


static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

