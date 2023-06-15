from enum import Enum

from pydantic import BaseModel


class Degree(Enum):
    BACHELOR = "bachelor"
    MASTER = "master"


class SemesterType(Enum):
    WINTERSEMESTER = "Wintersemester"
    SOMMERSEMESTER = "Sommersemester"


class Semester(BaseModel):
    id: str
    type: SemesterType
    year: int


class Course(BaseModel):
    id: str
    name: str
    degree: Degree
    shortcut_char: str
    shortcut_hyphen: str


class CourseInSemester(BaseModel):
    id: str
    course_id: str
    semester_id: str
    link: str


class Examen(BaseModel):
    id: str
    faculty: str
    course: Course
    semester: Semester
    memory_log: bool
    solution: bool
    professor: str
    file_id: str


class File(BaseModel):
    id: str
    name: str
    path: str
    size: int
    type: str
    contains_images: bool
    contains_text: bool
    text: str
    images_path: str
    url: str
