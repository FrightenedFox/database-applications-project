CREATE TABLE users
(
    usos_id          INTEGER                               NOT NULL
        CONSTRAINT users_pk
            PRIMARY KEY,
    first_name       TEXT,
    last_name        TEXT,
    joined_timestamp timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX users_usos_id_uindex
    ON users (usos_id);

CREATE TABLE group_types
(
    group_type_id   TEXT NOT NULL
        CONSTRAINT group_types_pk
            PRIMARY KEY,
    group_type_name TEXT
);

CREATE UNIQUE INDEX group_types_group_type_id_uindex
    ON group_types (group_type_id);

CREATE TABLE terms
(
    usos_term_id TEXT NOT NULL
        CONSTRAINT terms_pk
            PRIMARY KEY,
    term_name    TEXT,
    start_date   DATE NOT NULL,
    end_date     DATE NOT NULL
);

CREATE UNIQUE INDEX terms_usos_term_id_uindex
    ON terms (usos_term_id);

CREATE TABLE courses
(
    course_id   TEXT NOT NULL
        CONSTRAINT courses_pk
            PRIMARY KEY,
    course_name TEXT NOT NULL,
    term_id     TEXT NOT NULL
        CONSTRAINT courses_term_id_fk
            REFERENCES terms
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX courses_course_id_uindex
    ON courses (course_id);

CREATE TABLE buildings
(
    building_id   TEXT NOT NULL
        CONSTRAINT buildings_pk
            PRIMARY KEY,
    building_name TEXT,
    longitude     FLOAT,
    latitude      FLOAT
);

CREATE UNIQUE INDEX buildings_building_id_uindex
    ON buildings (building_id);

CREATE TABLE rooms
(
    room_id      TEXT    NOT NULL
        CONSTRAINT rooms_pk
            PRIMARY KEY,
    room_usos_id INTEGER NOT NULL,
    capacity     INTEGER DEFAULT 0,
    building_id  TEXT    NOT NULL
        CONSTRAINT room_building_id_fk
            REFERENCES buildings
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX rooms_room_id_uindex
    ON rooms (room_id);

CREATE UNIQUE INDEX rooms_room_usos_id_uindex
    ON rooms (room_usos_id);

CREATE TABLE teachers
(
    teacher_usos_id INTEGER NOT NULL
        CONSTRAINT teachers_pk
            PRIMARY KEY,
    first_name      TEXT    NOT NULL,
    last_name       TEXT    NOT NULL
);

CREATE UNIQUE INDEX teachers_usos_id_uindex
    ON teachers (teacher_usos_id);

CREATE TABLE study_programmes
(
    programme_id   TEXT NOT NULL
        CONSTRAINT study_programmes_pk
            PRIMARY KEY,
    programme_name TEXT
);

CREATE UNIQUE INDEX study_programmes_id_uindex
    ON study_programmes (programme_id);

CREATE TABLE user_programme
(
    user_id      INTEGER NOT NULL
        CONSTRAINT user_programme_user_id_fk
            REFERENCES users
            ON DELETE RESTRICT,
    programme_id TEXT    NOT NULL
        CONSTRAINT user_programme_programme_id_fk
            REFERENCES study_programmes
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX course_programme_uindex
    ON user_programme (user_id, programme_id);

CREATE TABLE usos_units
(
    usos_unit_id INTEGER NOT NULL
        CONSTRAINT usos_units_pk
            PRIMARY KEY,
    course       TEXT    NOT NULL
        CONSTRAINT usos_units_course_fk
            REFERENCES courses
            ON DELETE RESTRICT,
    group_type   TEXT    NOT NULL
        CONSTRAINT usos_units_group_type_fk
            REFERENCES group_types
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX usos_units_usos_unit_id_uindex
    ON usos_units (usos_unit_id);

CREATE TABLE unit_groups
(
    unit_group_id INTEGER GENERATED ALWAYS AS IDENTITY
        CONSTRAINT course_groups_pk
            PRIMARY KEY,
    usos_unit_id  INTEGER NOT NULL
        CONSTRAINT unit_groups_course_fk
            REFERENCES usos_units
            ON DELETE RESTRICT,
    group_number  INTEGER NOT NULL
);

CREATE UNIQUE INDEX unit_id_group_number_uindex
    ON unit_groups (usos_unit_id, group_number);

CREATE TABLE group_teacher
(
    unit_group INTEGER NOT NULL
        CONSTRAINT group_fk
            REFERENCES unit_groups
            ON DELETE RESTRICT,
    teacher    INTEGER NOT NULL
        CONSTRAINT teacher_fk
            REFERENCES teachers
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX group_teacher_uindex
    ON group_teacher (unit_group, teacher);

CREATE TABLE activities
(
    activity_id INTEGER GENERATED ALWAYS AS IDENTITY
        CONSTRAINT activities_pk
            PRIMARY KEY,
    start_time  timestamptz NOT NULL,
    end_time    timestamptz NOT NULL,
    room        TEXT
        CONSTRAINT activities_room_fk
            REFERENCES rooms
            ON DELETE RESTRICT,
    unit_group  INTEGER     NOT NULL
        CONSTRAINT activities_unit_group_fk
            REFERENCES unit_groups
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX activities_activity_id_uindex
    ON activities (activity_id);

CREATE UNIQUE INDEX activities_group_collision_uindex
    ON activities (unit_group, start_time, end_time);

CREATE TABLE course_manager
(
    course  TEXT    NOT NULL
        CONSTRAINT course_fk
            REFERENCES courses
            ON DELETE RESTRICT,
    manager INTEGER NOT NULL
        CONSTRAINT manager_fk
            REFERENCES teachers
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX course_manager_uindex
    ON course_manager (course, manager);

CREATE TABLE users_groups
(
    user_usos_id INTEGER NOT NULL
        CONSTRAINT users_fk
            REFERENCES users
            ON DELETE RESTRICT,
    group_id     INTEGER NOT NULL
        CONSTRAINT groups_fk
            REFERENCES unit_groups
            ON DELETE RESTRICT
);

COMMENT ON TABLE users_groups IS 'N groups - N users';

CREATE UNIQUE INDEX user_group_uindex
    ON users_groups (user_usos_id, group_id);
