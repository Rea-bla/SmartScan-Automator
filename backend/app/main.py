from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.search import router as search_router  # BU SATIRI EKLE

app = FastAPI(title="SmartScanAutomatorcd backend API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)  # BU SATIRI EKLE

@app.get("/")
def root():
    return {"status": "ok"}