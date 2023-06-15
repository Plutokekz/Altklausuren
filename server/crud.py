from typing import Optional, List, Type, Tuple

from fastapi import UploadFile
from sqlalchemy.orm import Session

from server import models, schemas
from server.models import Examen


def get_exman(examen_id: str, session: Session) -> Examen | None:
    return session.query(models.Examen).filter(models.Examen.id == examen_id).first()


def update_examen(examen: schemas.Examen, session: Session) -> tuple[Examen | None, str | None]:
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


def add_examen(examen: schemas.Examen, session: Session) -> tuple[Examen | None, str | None]:
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


def get_all_examens(session: Session, count: int = 100, offset: int = 0) -> list[Type[Examen]]:
    return session.query(models.Examen).limit(count).offset(offset).all()


def get_file(file_id: str, session: Session) -> Optional[models.File]:
    return session.query(models.File).filter(models.File.id == file_id).first()


def add_file(file_metadata: schemas.File, file: UploadFile, session: Session) -> tuple[models.File | None, str | None]:
    return None, None
