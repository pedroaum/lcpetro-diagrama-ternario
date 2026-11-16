"""API do Diagrama Ternário LCPETRO.

Guarda projetos e diagramas em PostgreSQL (variável DATABASE_URL) e serve a página
index.html. Sem DATABASE_URL usa um SQLite local (data/app.db), útil para testes.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if not DATABASE_URL:
    (ROOT / "data").mkdir(exist_ok=True)
    DATABASE_URL = f"sqlite:///{ROOT / 'data' / 'app.db'}"
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgres://"):]
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgresql://"):]

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), default="Projeto")
    position: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    diagrams: Mapped[list["Diagram"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="Diagram.position"
    )


class Diagram(Base):
    __tablename__ = "diagrams"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200), default="Diagrama")
    position: Mapped[int] = mapped_column(Integer, default=0)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    project: Mapped[Project] = relationship(back_populates="diagrams")


Base.metadata.create_all(engine)

app = FastAPI(title="Diagrama Ternário LCPETRO", docs_url="/api/docs", openapi_url="/api/openapi.json")


def db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


# ---------- esquemas ----------
class ProjectIn(BaseModel):
    name: Optional[str] = None
    position: Optional[int] = None


class DiagramIn(BaseModel):
    name: Optional[str] = None
    data: Optional[dict[str, Any]] = None
    project_id: Optional[int] = None
    position: Optional[int] = None


def diagram_out(d: Diagram) -> dict[str, Any]:
    return {
        "id": d.id,
        "project_id": d.project_id,
        "name": d.name,
        "position": d.position,
        "data": d.data or {},
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
    }


def project_out(p: Project, with_diagrams: bool = True) -> dict[str, Any]:
    out: dict[str, Any] = {
        "id": p.id,
        "name": p.name,
        "position": p.position,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }
    if with_diagrams:
        out["diagrams"] = [diagram_out(d) for d in p.diagrams]
    return out


# ---------- rotas ----------
@app.get("/api/health")
def health(s: Session = Depends(db)):
    s.execute(select(Project.id).limit(1))
    return {"ok": True, "db": engine.dialect.name}


@app.get("/api/workspace")
def workspace(s: Session = Depends(db)):
    projects = s.execute(select(Project).order_by(Project.position, Project.id)).scalars().all()
    stamp = max([p.updated_at for p in projects] + [d.updated_at for p in projects for d in p.diagrams], default=None)
    return {"projects": [project_out(p) for p in projects], "updated_at": stamp.isoformat() if stamp else None}


@app.post("/api/projects", status_code=201)
def create_project(body: ProjectIn, s: Session = Depends(db)):
    p = Project(name=body.name or "Projeto", position=body.position or 0)
    s.add(p)
    s.commit()
    return project_out(p)


@app.patch("/api/projects/{pid}")
def update_project(pid: int, body: ProjectIn, s: Session = Depends(db)):
    p = s.get(Project, pid)
    if not p:
        raise HTTPException(404, "projeto não encontrado")
    if body.name is not None:
        p.name = body.name
    if body.position is not None:
        p.position = body.position
    p.updated_at = now()
    s.commit()
    return project_out(p, with_diagrams=False)


@app.delete("/api/projects/{pid}", status_code=204)
def delete_project(pid: int, s: Session = Depends(db)):
    p = s.get(Project, pid)
    if p:
        s.delete(p)
        s.commit()
    return JSONResponse(status_code=204, content=None)


@app.post("/api/projects/{pid}/diagrams", status_code=201)
def create_diagram(pid: int, body: DiagramIn, s: Session = Depends(db)):
    if not s.get(Project, pid):
        raise HTTPException(404, "projeto não encontrado")
    d = Diagram(project_id=pid, name=body.name or "Diagrama", data=body.data or {}, position=body.position or 0)
    s.add(d)
    s.commit()
    return diagram_out(d)


@app.get("/api/diagrams/{did}")
def get_diagram(did: int, s: Session = Depends(db)):
    d = s.get(Diagram, did)
    if not d:
        raise HTTPException(404, "diagrama não encontrado")
    return diagram_out(d)


@app.put("/api/diagrams/{did}")
def update_diagram(did: int, body: DiagramIn, s: Session = Depends(db)):
    d = s.get(Diagram, did)
    if not d:
        raise HTTPException(404, "diagrama não encontrado")
    if body.name is not None:
        d.name = body.name
    if body.data is not None:
        d.data = body.data
    if body.project_id is not None:
        if not s.get(Project, body.project_id):
            raise HTTPException(404, "projeto de destino não encontrado")
        d.project_id = body.project_id
    if body.position is not None:
        d.position = body.position
    d.updated_at = now()
    s.commit()
    return diagram_out(d)


@app.delete("/api/diagrams/{did}", status_code=204)
def delete_diagram(did: int, s: Session = Depends(db)):
    d = s.get(Diagram, did)
    if d:
        s.delete(d)
        s.commit()
    return JSONResponse(status_code=204, content=None)


@app.get("/")
def index():
    return FileResponse(INDEX, media_type="text/html; charset=utf-8", headers={"Cache-Control": "no-cache"})
