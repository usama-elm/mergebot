import os
import logging
from routers import webhook
from litestar import Litestar, get

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# Health check endpoint
@get("/healthy")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        reload=os.environ.get("DEBUG") == "true",
    )


# Create FastAPI app
app = Litestar(
    [
        health_check,
    ]
)
