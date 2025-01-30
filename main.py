from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timezone


app = FastAPI()


class Response(BaseModel):
    email: str
    current_datetime: str
    github_url: str


@app.get("/", status_code=status.HTTP_200_OK, response_model=Response)
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
