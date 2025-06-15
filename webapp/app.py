from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os
import utils
import shadowsocks_methods as ss
from db import Database

def create_app():
    app = FastAPI()
    db = Database("users.db")  # или любой другой путь

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Условно подключаем HTTPS middleware
    if os.getenv("HTTPS_DISABLED", "false").lower() != "true":
        @app.middleware("http")
        async def force_https(request: Request, call_next):
            if request.url.scheme != "https":
                url = request.url.replace(scheme="https", netloc=f"{request.url.hostname}:443")
                return RedirectResponse(url, status_code=307)
            return await call_next(request)

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/connect/{key_value}")
    async def get_config(key_value: str):
        if not db.is_key_valid(key_value):
            raise HTTPException(status_code=403, detail="Invalid or expired key")
        server = db.load_balancer()
        access_url = ss.get_key_from_server(server, key_value)
        config = utils.parse_ss_url(access_url)
        if config is None:
            raise HTTPException(status_code=404, detail="Configuration not found for this key")
        return config

    return app
