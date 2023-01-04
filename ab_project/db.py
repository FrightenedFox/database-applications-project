import logging
from typing import Any

import pandas as pd
import psycopg2
import sqlalchemy

from ab_project.config.config import app_config


def get_nice_string(input_list: list[str]):
    return str(input_list).replace("'", "")[1:-1]


class UsosDB:
    """Makes the communication with the database easier."""

    sqlalchemy_engine: sqlalchemy.engine.base.Engine

    def __init__(self):
        self.conn = None
        self.is_connected = False

    def connect(self):
        """Connect to the PostgreSQL database server."""
        try:
            logging.info("Connecting to the PostgreSQL database...")
            self.conn = psycopg2.connect(**app_config.raw_sections["postgresql"])
            self.sqlalchemy_engine = sqlalchemy.create_engine(
                "postgresql+psycopg2://", creator=lambda: self.conn
            )

            # Display PostgreSQL version
            cur = self.conn.cursor()
            cur.execute("SELECT version()")
            logging.info(f"PostgreSQL version:\t{cur.fetchone()}")
            cur.close()

        except (Exception, psycopg2.DatabaseError):
            log_exception()

        if self.conn is not None:
            self.is_connected = True

    def disconnect(self):
        """Disconnect from the PostgreSQL database server."""
        if self.conn is not None:
            self.conn.close()
            self.sqlalchemy_engine.dispose()
            self.conn = None
            logging.info("Database connection closed.")
            self.is_connected = False
        else:
            # executes when there was no connection
            logging.warning(
                "Database was asked to be closed, but there was no connection."
            )
            logging.warning(
                f"self.is_connected set to False (before it was {self.is_connected})."
            )
            self.is_connected = False

    def row_exists(self, key_value: Any, key_column: str, table: str):
        """Checks whether there is a record with
        the same `key_value` in the specified `table`."""
        cur = self.conn.cursor()
        query = f"SELECT {key_column} " f"FROM   {table} " f"WHERE  {key_column} = %s;"
        cur.execute(query, (key_value,))
        ans = cur.fetchone()
        cur.close()
        logging.debug(
            f"Check if exists {key_column=} {key_value=} in {table}"
            f"Response {True if ans is not None else False}."
        )
        if ans is None:
            return False
        else:
            return True

    def create_user(self, usos_id: int | str, first_name: str, last_name: str):
        """Creates new record in the `users` table."""
        cur = self.conn.cursor()
        query = (
            "INSERT INTO users (usos_id, first_name, last_name, joined_timestamp) "
            "VALUES (%(usos_id)s, %(first_name)s, %(last_name)s, CURRENT_TIMESTAMP) "
            "ON CONFLICT (usos_id) DO UPDATE SET "
            "first_name = excluded.first_name, "
            "last_name = excluded.last_name;"
        )
        cur.execute(
            query,
            {"usos_id": usos_id, "first_name": first_name, "last_name": last_name},
        )
        self.conn.commit()
        cur.close()
        logging.debug(f"Add {usos_id=}, {first_name=}, {last_name=}")

    def upsert_course(self, course_id, course_name, term_id):
        """Updates or inserts a course."""
        cur = self.conn.cursor()
        query = (
            "INSERT INTO public.courses (course_id, course_name, term_id)"
            "VALUES (%(course_id)s, %(course_name)s, %(term_id)s)"
            "ON CONFLICT (course_id) "
            "DO UPDATE SET course_name = excluded.course_name;"
        )
        cur.execute(
            query,
            {"course_id": course_id, "course_name": course_name, "term_id": term_id},
        )
        self.conn.commit()
        cur.close()
        logging.debug(f"{course_name=}, {course_id=}, {term_id=}")

    def upsert_teacher(self, teacher_usos_id: int, first_name: str, last_name: str):
        """Updates or inserts a teacher."""
        cur = self.conn.cursor()
        query = (
            "INSERT INTO public.teachers "
            "(teacher_usos_id, first_name, last_name) "
            "VALUES (%(teacher_usos_id)s, %(first_name)s, %(last_name)s)"
            "ON CONFLICT (teacher_usos_id) "
            "DO UPDATE SET first_name = excluded.first_name,"
            "              last_name  = excluded.last_name;"
        )
        cur.execute(
            query,
            {
                "teacher_usos_id": teacher_usos_id,
                "first_name": first_name,
                "last_name": last_name,
            },
        )
        self.conn.commit()
        cur.close()
        logging.debug(f"{teacher_usos_id=}, {first_name=}, {last_name=}")

    def upsert_usos_units(self, usos_unit_id: int, course: str, group_type: str):
        """Updates or inserts an usos unit."""
        cur = self.conn.cursor()
        query = (
            "INSERT INTO public.usos_units (usos_unit_id, course, group_type) "
            "VALUES (%(usos_unit_id)s, %(course)s, %(group_type)s)"
            "ON CONFLICT (usos_unit_id) "
            "DO UPDATE SET course = excluded.course, "
            "group_type = excluded.group_type;"
        )
        cur.execute(
            query,
            {
                "usos_unit_id": usos_unit_id,
                "course": course,
                "group_type": group_type,
            },
        )
        self.conn.commit()
        cur.close()
        logging.debug(f"{usos_unit_id=}, {course=}")

    def upsert_group_types(self, group_type_id: str, group_type_name: str):
        """Updates or inserts a group type."""
        cur = self.conn.cursor()
        query = (
            "INSERT INTO public.group_types (group_type_id, group_type_name) "
            "VALUES (%(group_type_id)s, %(group_type_name)s)"
            "ON CONFLICT (group_type_id) "
            "DO UPDATE SET group_type_name = excluded.group_type_name;"
        )
        cur.execute(
            query, {"group_type_id": group_type_id, "group_type_name": group_type_name}
        )
        self.conn.commit()
        cur.close()
        logging.debug(f"{group_type_id=}, {group_type_name=}")

    def upsert_unit_group(self, usos_unit_id: int, group_number: int):
        """Updates or inserts a student group."""
        cur = self.conn.cursor()
        query = (
            "INSERT INTO public.unit_groups (usos_unit_id, group_number) "
            "VALUES (%(usos_unit_id)s, %(group_number)s) "
            "ON CONFLICT (usos_unit_id, group_number) "
            "DO UPDATE SET group_number=excluded.group_number "  # TODO: may be deleted in production
            "RETURNING unit_group_id;"
        )
        cur.execute(query, {"usos_unit_id": usos_unit_id, "group_number": group_number})
        ans_id = cur.fetchone()[0]
        self.conn.commit()
        cur.close()
        logging.debug(f"{usos_unit_id=}, {group_number=}.")
        return ans_id

    def upsert_activities(
            self, start_time: str, end_time: str, room: str, unit_group: int
    ):
        """Updates or inserts an activity."""
        if room == "":
            room = None
        cur = self.conn.cursor()
        query = (
            "INSERT INTO public.activities "
            "(start_time, end_time, room, unit_group) VALUES "
            "(%(start_time)s, %(end_time)s, %(room)s, %(unit_group)s)"
            "ON CONFLICT (start_time, end_time, unit_group) "
            "DO UPDATE SET room = excluded.room;"
        )
        cur.execute(
            query,
            {
                "start_time": start_time,
                "end_time": end_time,
                "room": room,
                "unit_group": unit_group,
            },
        )
        self.conn.commit()
        cur.close()
        logging.debug(f"{unit_group=} {start_time=} {end_time=} {room=}")

    def insert_group_teacher(self, unit_group: int, teacher: int):
        """Inserts a teacher if he doesn't exist."""
        cur = self.conn.cursor()
        query = (
            "INSERT INTO public.group_teacher (unit_group, teacher) "
            "VALUES (%(unit_group)s, %(teacher)s)"
            "ON CONFLICT (unit_group, teacher) DO NOTHING ;"
        )
        cur.execute(query, {"unit_group": unit_group, "teacher": teacher})
        self.conn.commit()
        cur.close()
        logging.debug(f"{unit_group=}, {teacher=}")

    def insert_course_manager(self, course_id: str, teacher_id: int):
        """Inserts a teacher if he doesn't exist."""
        cur = self.conn.cursor()
        query = (
            "INSERT INTO public.course_manager (course, manager) "
            "VALUES (%(course_id)s, %(teacher_id)s)"
            "ON CONFLICT (course, manager) DO NOTHING;"
        )
        cur.execute(query, {"course_id": course_id, "teacher_id": teacher_id})
        self.conn.commit()
        cur.close()
        logging.debug(f"{course_id=}, {teacher_id=}")

    def insert_user_programme(self, programme_id: str, user_id: int):
        """Inserts a teacher if he doesn't exist."""
        cur = self.conn.cursor()
        query = (
            "INSERT INTO public.user_programme (programme_id, user_id) "
            "VALUES (%(programme_id)s, %(user_id)s)"
            "ON CONFLICT (programme_id, user_id) DO NOTHING;"
        )
        cur.execute(query, {"programme_id": programme_id, "user_id": user_id})
        self.conn.commit()
        cur.close()
        logging.debug(f"{programme_id=}, {user_id=}")

    def insert_term(self, usos_term_id, term_name, start_date, end_date):
        """Inserts a term if it doesn't exist."""
        cur = self.conn.cursor()
        query = (
            "INSERT INTO public.terms (usos_term_id, "
            "term_name, start_date, end_date) "
            "VALUES (%(usos_term_id)s, %(term_name)s, "
            "%(start_date)s, %(end_date)s)"
            "ON CONFLICT (usos_term_id) DO NOTHING ;"
        )
        cur.execute(
            query,
            {
                "usos_term_id": usos_term_id,
                "term_name": term_name,
                "start_date": start_date,
                "end_date": end_date,
            },
        )
        self.conn.commit()
        cur.close()
        logging.debug(f"{usos_term_id=} {term_name=} {start_date=} {end_date=}")

    def insert_room(
            self, room_id: str, room_usos_id: int, capacity: int, building_id: str
    ):
        """Inserts a room if it doesn't exist."""
        cur = self.conn.cursor()
        query = (
            "INSERT INTO public.rooms (room_id, room_usos_id, capacity, building_id) "
            "VALUES (%(room_id)s, %(room_usos_id)s, %(capacity)s, %(building_id)s)"
            "ON CONFLICT (room_id) DO NOTHING ;"
        )
        cur.execute(
            query,
            {
                "room_id": room_id,
                "room_usos_id": room_usos_id,
                "capacity": capacity,
                "building_id": building_id,
            },
        )
        self.conn.commit()
        cur.close()
        logging.debug(f"{room_id=}, {room_usos_id=}, {capacity=}, {building_id=}")

    def insert_building(
            self, building_id: str, building_name: str, longitude: float, latitude: float
    ):
        """Inserts a room if it doesn't exist."""
        cur = self.conn.cursor()
        query = (
            "INSERT INTO public.buildings (building_id, building_name, longitude, latitude) "
            "VALUES (%(building_id)s, %(building_name)s, %(longitude)s, %(latitude)s)"
            "ON CONFLICT (building_id) DO NOTHING ;"
        )
        cur.execute(
            query,
            {
                "building_id": building_id,
                "building_name": building_name,
                "longitude": longitude,
                "latitude": latitude,
            },
        )
        self.conn.commit()
        cur.close()
        logging.debug(f"{building_id=}, {building_name=}, {longitude=}, {latitude=}")

    def insert_user_group(self, user_usos_id: int, unit_group_id: int):
        """Insert a user-unit_group connection if it doesn't exist."""
        cur = self.conn.cursor()
        group_id_query = (
            f"INSERT INTO public.users_groups (user_usos_id, group_id) "
            f"VALUES (%(user_usos_id)s, %(unit_group_id)s) "
            f"ON CONFLICT (user_usos_id, group_id) DO NOTHING;"
        )
        cur.execute(
            group_id_query,
            {"user_usos_id": user_usos_id, "unit_group_id": unit_group_id},
        )
        self.conn.commit()
        cur.close()
        logging.debug(f"{user_usos_id=}, {unit_group_id=}")

    def insert_study_programme(self, programme_id, programme_name):
        """Inserts a programme if it doesn't exist."""
        cur = self.conn.cursor()
        query = (
            "INSERT INTO public.study_programmes "
            "(programme_id, programme_name) "
            "VALUES (%(programme_id)s, %(programme_name)s)"
            "ON CONFLICT (programme_id) DO NOTHING ;"
        )
        cur.execute(
            query, {"programme_id": programme_id, "programme_name": programme_name}
        )
        self.conn.commit()
        cur.close()
        logging.debug(f"{programme_id=}, {programme_name=}")

    def get_unit_term_info(self, usos_term_id: str):
        cur = self.conn.cursor()
        query = (
            "SELECT terms.start_date, terms.end_date "
            "FROM terms "
            "WHERE terms.usos_term_id = %(usos_term_id)s;"
        )
        cur.execute(query, {"usos_term_id": usos_term_id})
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"{usos_term_id=}, term timings: {ans}")
        return ans

    def get_terms(self, programme_id: str):
        query = (
            "SELECT DISTINCT tr.usos_term_id, tr.term_name, tr.start_date, tr.end_date  "
            "FROM public.terms tr "
            "INNER JOIN courses c ON tr.usos_term_id = c.term_id "
            "INNER JOIN usos_units uun ON c.course_id = uun.course "
            "INNER JOIN unit_groups ugr ON uun.usos_unit_id = ugr.usos_unit_id "
            "INNER JOIN users_groups usg ON ugr.unit_group_id = usg.group_id "
            "INNER JOIN users u ON u.usos_id = usg.user_usos_id "
            "INNER JOIN user_programme upr ON u.usos_id = upr.user_id "
            "INNER JOIN study_programmes sp ON sp.programme_id = upr.programme_id "
            "WHERE sp.programme_id = %(programme_id)s;"
        )
        df = pd.read_sql(
            query, self.sqlalchemy_engine, params={"programme_id": programme_id}
        )
        logging.debug(f"Get terms for {programme_id=}.")
        return df

    def get_courses(self, programme_id: str, usos_term_id: str):
        query = (
            "SELECT DISTINCT c.course_id, c.course_name "
            "FROM public.terms tr "
            "INNER JOIN courses c ON tr.usos_term_id = c.term_id "
            "INNER JOIN usos_units uun ON c.course_id = uun.course "
            "INNER JOIN unit_groups ugr ON uun.usos_unit_id = ugr.usos_unit_id "
            "INNER JOIN users_groups usg ON ugr.unit_group_id = usg.group_id "
            "INNER JOIN users u ON u.usos_id = usg.user_usos_id "
            "INNER JOIN user_programme upr ON u.usos_id = upr.user_id "
            "INNER JOIN study_programmes sp ON sp.programme_id = upr.programme_id "
            "WHERE sp.programme_id = %(programme_id)s "
            "  AND tr.usos_term_id = %(usos_term_id)s;"
        )
        df = pd.read_sql(
            query,
            self.sqlalchemy_engine,
            params={"programme_id": programme_id, "usos_term_id": usos_term_id},
        )
        logging.debug(f"Get terms for {programme_id=}, {usos_term_id=}.")
        return df

    def get_group_types(self, usos_term_id: str, course_id: str):
        query = (
            "SELECT grt.group_type_id, grt.group_type_name "
            "FROM public.group_types grt "
            "INNER JOIN usos_units uu ON grt.group_type_id = uu.group_type "
            "INNER JOIN courses c ON c.course_id = uu.course "
            "INNER JOIN terms tr ON tr.usos_term_id = c.term_id "
            "WHERE c.course_id = %(course_id)s "
            "  AND tr.usos_term_id = %(usos_term_id)s;"
        )
        df = pd.read_sql(
            query,
            self.sqlalchemy_engine,
            params={"usos_term_id": usos_term_id, "course_id": course_id},
        )
        logging.debug(f"Get group types for {course_id=}, {usos_term_id=}.")
        return df

    def get_unit_groups(self, usos_term_id: str, course_id: str, group_type: str):
        query = (
            "SELECT ung.unit_group_id, ung.group_number "
            "FROM public.unit_groups ung "
            "INNER JOIN usos_units uu ON uu.usos_unit_id = ung.usos_unit_id "
            "INNER JOIN courses c ON c.course_id = uu.course "
            "INNER JOIN terms tr ON tr.usos_term_id = c.term_id "
            "WHERE uu.group_type = %(group_type)s"
            "  AND c.course_id =  %(course_id)s"
            "  AND tr.usos_term_id = %(usos_term_id)s;"
        )
        df = pd.read_sql(
            query,
            self.sqlalchemy_engine,
            params={
                "usos_term_id": usos_term_id,
                "course_id": course_id,
                "group_type": group_type,
            },
        )
        logging.debug(
            f"Get unit group for {course_id=}, {usos_term_id=} {group_type=}."
        )
        return df

    def get_users(self, unit_group_id: int):
        query = (
            "SELECT u.usos_id, u.first_name, u.last_name "
            "FROM public.users u "
            "         INNER JOIN users_groups ugr ON u.usos_id = ugr.user_usos_id "
            "         INNER JOIN unit_groups ung ON ung.unit_group_id = ugr.group_id "
            "WHERE ung.unit_group_id = %(unit_group_id)s;"
        )
        df = pd.read_sql(
            query, self.sqlalchemy_engine, params={"unit_group_id": unit_group_id}
        )
        logging.debug(f"Get users for {unit_group_id=}.")
        return df

    def get_unit_group_teacher(self, unit_group_id: int):
        cur = self.conn.cursor()
        query = (
            "SELECT t.teacher_usos_id, t.first_name, t.last_name "
            "FROM teachers t "
            "         INNER JOIN group_teacher gt ON t.teacher_usos_id = gt.teacher "
            "         INNER JOIN unit_groups ug ON gt.unit_group = ug.unit_group_id "
            "WHERE unit_group_id = %(unit_group_id)s;"
        )
        cur.execute(query, {"unit_group_id": unit_group_id})
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"Get unit group teacher {unit_group_id=}.")
        return ans

    def get_unit_group_activities(self, unit_group_id: int):
        query = (
            "SELECT * "
            "FROM activities a "
            "         INNER JOIN unit_groups ug ON a.unit_group = ug.unit_group_id "
            "WHERE ug.unit_group_id = %(unit_group_id)s;"
        )
        df = pd.read_sql(
            query, self.sqlalchemy_engine, params={"unit_group_id": unit_group_id}
        )
        logging.debug(f"Get unit group activities {unit_group_id=}.")
        return df

    def delete_activity(self, activity_id: int):
        cur = self.conn.cursor()
        query = (
            "DELETE "
            "FROM activities "
            "WHERE activity_id = %(activity_id)s;"
        )
        cur.execute(query, {"activity_id": activity_id})
        self.conn.commit()
        cur.close()
        logging.debug(f"Delete activity {activity_id=}.")

    def get_all_from_table(self, table: str, column: str = "*"):
        cur = self.conn.cursor()
        query = f"SELECT {column} FROM {table};"
        cur.execute(query)
        ans = cur.fetchall()
        cur.close()
        logging.debug(f"Get {column} from {table}.")
        return ans

    def pandas_get_all_from_table(self, table: str, column: str = "*"):
        query = f"SELECT {column} FROM {table};"
        df = pd.read_sql(query, self.sqlalchemy_engine)
        logging.debug(f"Pandas get {column} from {table}.")
        return df

    def run_function(self, function_name: str, params: list | None = None):
        cur = self.conn.cursor()
        cur.callproc(function_name, params)
        self.conn.commit()
        ans = cur.ferchall()
        cur.close()
        logging.debug(
            f"Call function '{function_name}' with the following params: {params}."
        )
        return ans

    def call_procedure(
            self, procedure_name_with_s_placeholders: str, params: list | None = None
    ):
        cur = self.conn.cursor()
        cur.execute(f"CALL {procedure_name_with_s_placeholders};", params)
        ans = cur.fetchone()
        self.conn.commit()
        cur.close()
        logging.debug(
            f"Call procedure '{procedure_name_with_s_placeholders}' with the following params: {params}."
        )
        return ans

    def upsert_returning(
            self,
            table: str,
            items: list[dict[str, Any]] | dict[str, Any],
            update_columns: list[str] | str | None = None,
            returning_columns: list[str] | str | None = None,
    ):
        """Updates or inserts any table."""
        if isinstance(items, dict):
            items = [items]
        if isinstance(update_columns, str):
            update_columns = [update_columns]
        if isinstance(returning_columns, str):
            returning_columns = [returning_columns]

        column_list = get_nice_string(list(items[0].keys()))

        values_list = ""
        for items_part in items:
            values_list += "\n\t( %s )," % get_nice_string(list(items_part.values()))
        values_list = values_list[-1]

        if update_columns is not None:
            upsert_query = "ON CONFLICT DO UPDATE SET"
            for update_column in update_columns:
                upsert_query += f"\n\t{update_column} = excluded.{update_column},"
            upsert_query = upsert_query[:-1]
        else:
            upsert_query = ""

        if returning_columns is not None:
            return_query = "RETURNING %s" % get_nice_string(returning_columns)
        else:
            return_query = ""

        query = (
            f"INSERT INTO {table} ({column_list}) VALUES {values_list} "
            f"{upsert_query} {return_query};"
        )
        logging.debug(query)
        cur = self.conn.cursor()
        cur.execute(query)
        ans = cur.fetchall()
        cur.close()
        return ans

    def get_specific_value(self, where, where_value, col_name, table="users"):
        """Retrieves a specific value from a specific row."""
        cur = self.conn.cursor()
        query = f"SELECT {col_name} " f"FROM   {table} " f"WHERE  {where} = %s;"
        cur.execute(query, (where_value,))
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"{query=}\t{where_value=}")
        return ans

    def update_specific_value(
            self, where, where_value, col_name, col_name_value, table="users"
    ):
        """Updates a specific value from a specific row."""
        cur = self.conn.cursor()
        query = (
            f"UPDATE    {table} "
            f"SET       {col_name} = %(col_name_value)s "
            f"WHERE     {where} = %(where_value)s; "
        )
        cur.execute(
            query,
            {
                "col_name_value": col_name_value,
                "where_value": where_value,
            },
        )
        self.conn.commit()
        cur.close()
        logging.debug(f"{query=}\t{col_name_value=}, {where_value=}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    db = UsosDB()
    db.connect()
    print(type(db.conn))
    db.disconnect()
