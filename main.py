from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Public Notes API",
    description="A simple public API. Interactive docs at /docs",
    version="1.0.0",
)

# Allow requests from any website/app (public access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store (resets on restart; swap for a database later)
notes: dict[str, dict] = {}


class NoteIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field("", max_length=2000)


@app.get("/")
def root():
    return {"message": "API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/notes")
def list_notes():
    return list(notes.values())


@app.get("/notes/{note_id}")
def get_note(note_id: str):
    if note_id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")
    return notes[note_id]


@app.post("/notes", status_code=201)
def create_note(note: NoteIn):
    note_id = str(uuid4())
    notes[note_id] = {
        "id": note_id,
        **note.model_dump(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return notes[note_id]


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: str):
    if notes.pop(note_id, None) is None:
        raise HTTPException(status_code=404, detail="Note not found")
