from sqlalchemy import String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Semester(Base):
    __tablename__ = "semesters"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    type: Mapped[str] = mapped_column(String)
    year: Mapped[str] = mapped_column(String(7))

    def __repr__(self):
        return f"Semester(id={self.id!r}, type={self.type!r}, year={self.year!r})"


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    degree: Mapped[str] = mapped_column(String)
    shortcut_char: Mapped[str] = mapped_column(String, index=True)
    shortcut_hyphen: Mapped[str] = mapped_column(String, index=True)

    def __repr__(self):
        return (
            f"Course(id={self.id!r}, name={self.name!r}, degree={self.degree!r}) "
            f"shortcut_char={self.shortcut_char!r}, shortcut_hyphen={self.shortcut_hyphen!r})"
        )


class CourseInSemester(Base):
    __tablename__ = "courses_in_semester"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id"))
    semester_id: Mapped[str] = mapped_column(ForeignKey("semesters.id"))
    link: Mapped[str] = mapped_column(String, nullable=True)

    def __repr__(self):
        return f"CourseInSemester(id={self.id!r}, course_id={self.course_id!r}, semester_id={self.semester_id!r}, link={self.link!r})"


class File(Base):
    __tablename__ = "files"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    path: Mapped[str] = mapped_column(String(500))
    size: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String(10))
    contains_images: Mapped[bool] = mapped_column(Boolean)
    contains_text: Mapped[bool] = mapped_column(Boolean)
    text: Mapped[str] = mapped_column(String(50000), nullable=True)
    images_path: Mapped[str] = mapped_column(String(500), nullable=True)
    url: Mapped[str] = mapped_column(String(256))

    def __repr__(self) -> str:
        return (
            f"File(id={self.id!r}, name={self.name!r}, path={self.path!r}, size={self.size!r}, type={self.type!r},"
            f" url={self.url}), contains_images={self.contains_images!r}, contains_text={self.contains_text!r}, "
        )


class Examen(Base):
    __tablename__ = "exams"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    faculty: Mapped[str] = mapped_column(String(256))
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id"))
    semester_id: Mapped[str] = mapped_column(ForeignKey("semesters.id"))
    memory_log: Mapped[bool] = mapped_column(Boolean)
    solution: Mapped[bool] = mapped_column(Boolean)
    professor: Mapped[str] = mapped_column(String(256))
    file_id: Mapped[str] = mapped_column(ForeignKey("files.id"))

    def __repr__(self) -> str:
        return (
            f"Exam(id={self.id!r}, faculty={self.faculty!r}, course_id={self.course_id!r}, semester_id={self.semester_id!r}, "
            f"memory_log={self.memory_log!r}, solution={self.solution!r}, professor={self.professor!r}, file_id={self.file_id!r})"
        )
