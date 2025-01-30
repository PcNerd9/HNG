from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone


app = FastAPI()


@app.get("/", status_code=status.HTTP_200_OK)
async def home():
    return JSONResponse(
        content={
            "email": "Ajayihabeeb977@gmail.com",
            "current_datetime": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "github_url": "https://github.com/PcNerd9/Hng",
        }
    )
