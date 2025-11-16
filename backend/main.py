from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import recommend, recommendation_history, crop_suitability, suitability_history
app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # or specify your frontend URL e.g. ["http://localhost:5173"]
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*","Authorization","Content-Type"]
)

app.include_router(recommend.router)
app.include_router(recommendation_history.router)
app.include_router(crop_suitability.router)
app.include_router(suitability_history.router)
# app.include_router(suitability)


@app.get("/")
def root():
    return {"message":"CropWise is running "}