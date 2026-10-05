from fastapi import FastAPI
from app.api.routes.document import router as document_router
from app.api.routes.source_document import router as source_document_router

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(document_router)
app.include_router(source_document_router)
