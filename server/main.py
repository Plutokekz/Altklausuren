import os
from typing import List

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import schemas
from server.database import SessionLocal
import crud

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/examen/add", response_model=schemas.Examen)
async def add_examen(examen: schemas.Examen, session: Session = Depends(get_session)):
    examen, error = crud.add_examen(examen, session)
    if error is not None:
        raise HTTPException(status_code=404, detail=error)
    return examen


@app.post("/examen/update/{examen_id}", response_model=schemas.Examen)
async def update_examen(
    examen: schemas.Examen, session: Session = Depends(get_session)
):
    examen, error = crud.update_examen(examen, session)
    if error is not None:
        raise HTTPException(status_code=404, detail=error)
    return examen


@app.get("/examen/get/{examen_id}", response_model=schemas.Examen)
async def get_examen(examen_id: str, session: Session = Depends(get_session)):
    examen = crud.get_exman(examen_id, session)
    if examen is None:
        raise HTTPException(
            status_code=404, detail=f"Error no  examen id {examen_id} found"
        )
    return examen


@app.get("/examen/all", response_model=List[schemas.Examen])
async def get_all_examen(
    count: int = 100, offset: int = 0, session: Session = Depends(get_session)
):
    examen = crud.get_all_examens(session, count, offset)
    if examen is None or len(examen) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Error no examen available with count {count} and offset {offset} found",
        )
    return examen


@app.get("/file/get/{file_id}", response_model=schemas.File)
async def get_file(file_id: str, session: Session = Depends(get_session)):
    file = crud.get_file(file_id, session)
    if file is None:
        raise HTTPException(status_code=404, detail=f"Error no file id {file_id} found")
    return file


@app.post("/file/add", response_model=schemas.File)
async def add_file(
    file_metadata: schemas.File,
    file: UploadFile,
    session: Session = Depends(get_session),
):
    file, error = crud.add_file(file_metadata, file, session)
    if error is not None:
        raise HTTPException(status_code=404, detail=error)
    return file


@app.get("/course/get/{course_id}", response_model=schemas.Course)
async def get_course(course_id: str, session: Session = Depends(get_session)):
    course = crud.get_course(course_id, session)
    if course is None:
        raise HTTPException(
            status_code=404, detail=f"Error no course id {course_id} found"
        )
    return course


@app.get("/course/all", response_model=List[schemas.Course])
async def get_all_courses(
    count: int = 100, offset: int = 0, session: Session = Depends(get_session)
):
    courses = crud.get_all_courses(session, count, offset)
    if courses is None or len(courses) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Error no courses available with offset {offset} and count {count}",
        )
    return courses


@app.get("/semester/get/{semester_id}", response_model=schemas.Semester)
async def get_semester(semester_id: str, session: Session = Depends(get_session)):
    semester = crud.get_semester(semester_id, session)
    if semester is None:
        raise HTTPException(
            status_code=404, detail=f"Error no semester id {semester_id} found"
        )
    return semester


@app.get("/semester/all", response_model=List[schemas.Semester])
async def get_all_semester(
    count: int = 100, offset: int = 0, session: Session = Depends(get_session)
):
    semesters = crud.get_all_semester(session, count, offset)
    if semesters is None or len(semesters) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Error no semesters available with offset {offset} and count {count}",
        )
    return semesters


if __name__ == "__main__":
    uvicorn.run(app)
