from sqlalchemy import Column, String, Date, Integer, DateTime

from db_utils import Base


class Terms(Base):
    __tablename__ = "terms"

    usos_term_id = Column(String, primary_key=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    term_name = Column(String)

    def __repr__(self) -> str:
        return (f"Term(usos_term_id={self.usos_term_id}, start_date={self.start_date}, "
                f"end_date={self.end_date}, term_name={self.term_name})")


class StudyProgrammes(Base):
    __tablename__ = "study_programmes"

    programme_id = Column(String, primary_key=True)
    programme_name = Column(String)

    def __repr__(self) -> str:
        return f"StudyProgramme(programme_id={self.programme_id}, programme_name={self.programme_name})"


class Courses(Base):
    __tablename__ = "courses"

    course_id = Column(String, primary_key=True)
    term_id = Column(String, nullable=False)
    course_name = Column(String, nullable=False)

    def __repr__(self) -> str:
        return (f"Course(course_id={self.course_id}, term_id={self.term_id}, "
                f"course_name={self.course_name})")


class GroupTypes(Base):
    __tablename__ = "group_types"

    group_type_id = Column(String, primary_key=True)
    group_type_name = Column(String)
    max_group_size = Column(Integer)

    def __repr__(self) -> str:
        return (f"GroupType(group_type_id={self.group_type_id}, group_type_name={self.group_type_name}, "
                f"max_group_size={self.max_group_size})")


class CourseProgramme(Base):
    __tablename__ = "course_programme"

    course_id = Column(String, nullable=False)
    programme_id = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"CourseProgramme(course_id={self.course_id}, programme_id={self.programme_id})"


class UsosUnits(Base):
    __tablename__ = "usos_units"

    usos_unit_id = Column(Integer, primary_key=True)
    course = Column(String, nullable=False)
    group_type = Column(String, nullable=False)

    def __repr__(self) -> str:
        return (f"UsosUnit(usos_unit_id={self.usos_unit_id}, course={self.course}, "
                f"group_type={self.group_type})")


class Rooms(Base):
    __tablename__ = "rooms"

    room_id = Column(String, primary_key=True)
    capacity = Column(Integer)

    def __repr__(self) -> str:
        return f"Room(room_id={self.room_id}, capacity={self.capacity}"


class Users(Base):
    __tablename__ = "users"

    usos_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    joined_timestamp = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return (f"User(usos_id={self.usos_id}, joined_timestamp={self.joined_timestamp}, "
                f"first_name={self.first_name}, last_name={self.last_name})")


class UnitGroups(Base):
    __tablename__ = "unit_groups"

    unit_group_id = Column(Integer, primary_key=True)
    usos_unit_id = Column(Integer, nullable=False)
    group_number = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return (f"UnitGroup(unit_group_id={self.unit_group_id}, usos_unit_id={self.usos_unit_id}, "
                f"group_number={self.group_number})")


class Teachers(Base):
    __tablename__ = "teachers"

    teacher_usos_id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String)
    title = Column(String)
    private_room = Column(String)

    def __repr__(self) -> str:
        return (f"Teacher(teacher_usos_id={self.teacher_usos_id}, first_name={self.first_name}, "
                f"last_name={self.last_name}, email={self.email}, title={self.title}, "
                f"private_room={self.private_room})")


class UsersGroups(Base):
    __tablename__ = "users_groups"

    user_usos_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"UserGroup(user_usos_is={self.user_usos_id}, group_id={self.group_id}"


class Activities(Base):
    __tablename__ = "activities"

    activity_id = Column(Integer, primary_key=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    room = Column(String, nullable=False)
    unit_group = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return (f"Activity(activity_id={self.activity_id}, start_time={self.start_time}, "
                f"end_time={self.end_time}, room={self.room}, unit_group={self.unit_group})")


class GroupTeacher(Base):
    __tablename__ = "group_teacher"

    unit_group = Column(Integer, nullable=False)
    teacher = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"GroupTeacher(unit_group={self.unit_group}, teacher={self.teacher}"


class CourseManager(Base):
    __tablename__ = "course_manager"

    course = Column(String, nullable=False)
    manager = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"CourseManager(course={self.course}, manager={self.manager}"
