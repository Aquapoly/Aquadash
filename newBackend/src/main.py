from fastapi import FastAPI
from src.api.v1.api_router import api_router
from src.features.database.database import default_populate, get_db, Base, engine

from fastapi.middleware.cors import CORSMiddleware
# from fastapi_utils.openapi import simplify_operation_ids
from contextlib import asynccontextmanager


app = FastAPI(title="Aquadash API")

@app.get("/", tags=["Health Check"])
def health_check():
    """
    Health check endpoint to ensure the API is running.
    """
    return {"status": "ok", "message": "Aquadash API is running."}


Base.metadata.create_all(bind=engine)


sensors_data = dict()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())  
    default_populate(db)  
    yield


app = FastAPI(lifespan=lifespan)

origins = ["http://localhost", "http://localhost:4200", "http://127.0.0.1:4200", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Include the main API router with a prefix
app.include_router(api_router, prefix="/api/v1")







