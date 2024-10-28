from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from routes.users import user_route
from routes.routines import routines_route
from routes.tags import tag_route
from decouple import config
from database import create_base_routine


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

@app.on_event("startup")
async def startup_event():
    await create_base_routine()

app.include_router(user_route)
app.include_router(routines_route)
app.include_router(tag_route)
