CREATE TABLE users
(
    usos_id          integer                               NOT NULL
        CONSTRAINT users_pk
            PRIMARY KEY,
    first_name       text,
    last_name        text,
    joined_timestamp timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX users_usos_id_uindex
    ON users (usos_id);

CREATE TABLE group_types
(
    group_type_id   text NOT NULL
        CONSTRAINT group_types_pk
            PRIMARY KEY,
    group_type_name text,
    max_group_size  integer
);

CREATE UNIQUE INDEX group_types_group_type_id_uindex
    ON group_types (group_type_id);

CREATE TABLE terms
(
    usos_term_id text NOT NULL
        CONSTRAINT terms_pk
            PRIMARY KEY,
    term_name    text,
    start_date   date NOT NULL,
    end_date     date NOT NULL
);

CREATE UNIQUE INDEX terms_usos_term_id_uindex
    ON terms (usos_term_id);

CREATE TABLE courses
(
    course_id   text NOT NULL
        CONSTRAINT courses_pk
            PRIMARY KEY,
    course_name text NOT NULL,
    term_id     text NOT NULL
        CONSTRAINT courses_term_id_fk
            REFERENCES terms
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX courses_course_id_uindex
    ON courses (course_id);

CREATE TABLE rooms
(
    room_id  text NOT NULL
        CONSTRAINT rooms_pk
            PRIMARY KEY,
    capacity integer DEFAULT 0
);

CREATE UNIQUE INDEX rooms_room_id_uindex
    ON rooms (room_id);

CREATE TABLE teachers
(
    teacher_usos_id integer NOT NULL
        CONSTRAINT teachers_pk
            PRIMARY KEY,
    first_name      text    NOT NULL,
    last_name       text    NOT NULL,
    email           text,
    title           text,
    private_room    text
        CONSTRAINT teachers_private_room_fk
            REFERENCES rooms
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX teachers_usos_id_uindex
    ON teachers (teacher_usos_id);

CREATE TABLE study_programmes
(
    programme_id   text NOT NULL
        CONSTRAINT study_programmes_pk
            PRIMARY KEY,
    programme_name text
);

CREATE UNIQUE INDEX study_programmes_id_uindex
    ON study_programmes (programme_id);

CREATE TABLE course_programme
(
    course_id      text NOT NULL
        CONSTRAINT courses_fk
            REFERENCES courses
            ON DELETE RESTRICT,
    programme_id text    NOT NULL
        CONSTRAINT programme_fk
            REFERENCES study_programmes
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX course_programme_uindex
    ON course_programme (course_id, programme_id);

CREATE TABLE usos_units
(
    usos_unit_id integer NOT NULL
        CONSTRAINT usos_units_pk
            PRIMARY KEY,
    course       text    NOT NULL
        CONSTRAINT usos_units_course_fk
            REFERENCES courses
            ON DELETE RESTRICT,
    group_type   text    NOT NULL
        CONSTRAINT usos_units_group_type_fk
            REFERENCES group_types
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX usos_units_usos_unit_id_uindex
    ON usos_units (usos_unit_id);

CREATE TABLE unit_groups
(
    unit_group_id integer GENERATED ALWAYS AS IDENTITY
        CONSTRAINT course_groups_pk
            PRIMARY KEY,
    usos_unit_id  integer NOT NULL
        CONSTRAINT unit_groups_course_fk
            REFERENCES usos_units
            ON DELETE RESTRICT,
    group_number  integer NOT NULL
);

CREATE UNIQUE INDEX unit_id_group_number_uindex
    ON unit_groups (usos_unit_id, group_number);

CREATE TABLE group_teacher
(
    unit_group integer NOT NULL
        CONSTRAINT group_fk
            REFERENCES unit_groups
            ON DELETE RESTRICT,
    teacher    integer NOT NULL
        CONSTRAINT teacher_fk
            REFERENCES teachers
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX group_teacher_uindex
    ON group_teacher (unit_group, teacher);

CREATE TABLE activities
(
    activity_id integer GENERATED ALWAYS AS IDENTITY
        CONSTRAINT activities_pk
            PRIMARY KEY,
    start_time  timestamptz NOT NULL,
    end_time    timestamptz NOT NULL,
    room        text        NOT NULL
        CONSTRAINT activities_room_fk
            REFERENCES rooms
            ON DELETE RESTRICT,
    unit_group  integer     NOT NULL
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
    course  text    NOT NULL
        CONSTRAINT course_fk
            REFERENCES courses
            ON DELETE RESTRICT,
    manager integer NOT NULL
        CONSTRAINT manager_fk
            REFERENCES teachers
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX course_manager_uindex
    ON course_manager (course, manager);

CREATE TABLE users_groups
(
    user_usos_id  integer NOT NULL
        CONSTRAINT users_fk
            REFERENCES users
            ON DELETE RESTRICT,
    group_id integer NOT NULL
        CONSTRAINT groups_fk
            REFERENCES unit_groups
            ON DELETE RESTRICT
);

COMMENT ON TABLE users_groups IS 'N groups - N users';

CREATE UNIQUE INDEX user_group_uindex
    ON users_groups (user_usos_id, group_id);
