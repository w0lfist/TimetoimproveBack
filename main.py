from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from routes.users import user_route
from routes.routines import routines_route
from routes.tags import tag_route
from decouple import config
from database import create_base_routine
import os
import uvicorn

app = FastAPI()

frontend_url = config('FRONTEND_URL')

app.add_middleware(
    CORSMiddleware,
    allow_origins= frontend_url,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def welcome():
    return {"message": "Welcome tu Time to Improve"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

@app.on_event("startup")
async def startup_event():
    await create_base_routine()

app.include_router(user_route)
app.include_router(routines_route)
app.include_router(tag_route)
