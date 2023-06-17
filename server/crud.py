from pathlib import Path
from typing import Optional, List, Type, Tuple

from fastapi import UploadFile
from sqlalchemy.orm import Session

from server import models, schemas
from server.models import Examen
from server.pdf_processor import PDFProcessor


def get_exman(examen_id: str, session: Session) -> Examen | None:
    return session.query(models.Examen).where(models.Examen.id == examen_id).first()


def update_examen(
        examen: schemas.Examen, session: Session
) -> tuple[Examen | None, str | None]:
    queried_examen: Optional[models.Examen] = (
        session.query(models.Examen).where(models.Examen.id == examen.id).first()
    )
    if queried_examen is None:
        return None, "Examen not found"

    queried_course: Optional[models.Course] = (
        session.query(models.Course).where(models.Course.id == examen.course.id).first()
    )

    if queried_course is None:
        return None, "Course not found"

    queried_semester: Optional[models.Semester] = (
        session.query(models.Semester)
        .where(models.Semester.id == examen.semester.id)
        .first()
    )

    if queried_semester is None:
        return None, "Semester not found"

    queried_examen.course_id = queried_course.id
    queried_examen.semester_id = queried_semester.id
    queried_examen.faculty = examen.faculty
    queried_examen.course = examen.course
    queried_examen.semester = examen.semester
    queried_examen.memory_log = examen.memory_log
    queried_examen.solution = examen.solution
    queried_examen.professor = examen.professor
    queried_examen.file_id = examen.file_id
    session.refresh(queried_examen)
    session.commit()
    return queried_examen, None


def add_examen(
        examen: schemas.Examen, session: Session
) -> tuple[Examen | None, str | None]:
    if (
            session.query(models.Examen).where(models.Examen.id == examen.id).first()
            is not None
    ):
        return None, "Examen already exists"

    queried_course: Optional[models.Course] = (
        session.query(models.Course).where(models.Course.id == examen.course.id).first()
    )

    if queried_course is None:
        return None, "Course not found"

    queried_semester: Optional[models.Semester] = (
        session.query(models.Semester)
        .where(models.Semester.id == examen.semester.id)
        .first()
    )

    if queried_semester is None:
        return None, "Semester not found"

    db_examen = models.Examen(
        id=examen.id,
        faculty=examen.faculty,
        course=examen.course,
        semester=examen.semester,
        memory_log=examen.memory_log,
        solution=examen.solution,
        professor=examen.professor,
        file_id=examen.file_id,
        course_id=queried_course.id,
        semester_id=queried_semester.id,
    )

    session.add(db_examen)
    session.refresh(db_examen)
    session.commit()
    return db_examen, None


def get_all_examens(
        session: Session, count: int = 100, offset: int = 0
) -> list[Type[Examen]]:
    return session.query(models.Examen).limit(count).offset(offset).all()


def get_file(file_id: str, session: Session) -> Optional[models.File]:
    return session.query(models.File).where(models.File.id == file_id).first()


def add_file(
        file_metadata: schemas.File, file: UploadFile, session: Session
) -> tuple[models.File | None, str | None]:
    if session.query(models.File).where(models.File.id == file_metadata.id).first() is not None:
        return None, "File already exists"

    path = Path(file_metadata.path) / file_metadata.name
    with open(path, "wb") as f:
        f.write(file.file.read())

    text = PDFProcessor.extract_text_from_pdf(path)
    contains_text = False
    if text is not None and text:
        contains_text = True
    num_of_images = PDFProcessor.pdf_pages_to_images(path, path.parent / file_metadata.name)
    contains_images = False
    if num_of_images > 0:
        contains_images = True

    db_file = models.File(
        id=file_metadata.id,
        name=file_metadata.name,
        type=file_metadata.type,
        path=file_metadata.path,
        size=file_metadata.size,
        contains_images=contains_images,
        contains_text=contains_text,
        text=text,
        images_path=file_metadata.images_path,
        url=file_metadata.url
    )
    session.query(db_file)
    session.commit()
    session.refresh(db_file)

    return db_file, None


def get_course(course_id: str, session: Session) -> Optional[models.Course]:
    return session.query(models.Course).where(models.Course.id == course_id).first()


def get_semester(semester_id: str, session: Session) -> Optional[models.Semester]:
    return (
        session.query(models.Semester).where(models.Semester.id == semester_id).first()
    )


def get_all_semester(
        session: Session, count: int, offset: int
) -> list[Type[models.Semester]]:
    return session.query(models.Semester).limit(count).offset(offset).all()


def get_all_courses(
        session: Session, count: int, offset: int
) -> list[Type[models.Course]]:
    return session.query(models.Course).limit(count).offset(offset).all()
