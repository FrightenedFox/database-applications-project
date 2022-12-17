--1 Zmiana prowadzacego
CREATE OR REPLACE PROCEDURE zmien_prowadzacego(grupa_id unit_groups.unit_group_id%TYPE,
                                               wykladowca_id group_teacher.teacher%TYPE)
    LANGUAGE plpgsql
AS
$$
DECLARE
    poczatek timestamp;
    koniec   timestamp;
BEGIN
    SELECT start_time, end_time
    INTO poczatek, koniec
    FROM activities
    WHERE unit_group = grupa_id;
    IF zajecia_wykladowcy_w_danym_czasie(wykladowca_id, poczatek, koniec) = TRUE
    THEN
        UPDATE group_teacher
        SET teacher = wykladowca_id
        WHERE unit_group = grupa_id;
        RAISE NOTICE 'Wykladowca zostal zmieniony';
    ELSE
        RAISE NOTICE 'Wykladowca ma wtedy zajecia';
    END IF;
END
$$;
CALL zmien_prowadzacego(18, 27061);
--2 Dodanie nowych zajec
CREATE OR REPLACE PROCEDURE dodaj_nowe_zajecia(grupa_id unit_groups.unit_group_id%TYPE,
                                               wykladowca_id group_teacher.teacher%TYPE, sala rooms.room_id%TYPE,
                                               czas_rozpoczecia activities.start_time%TYPE,
                                               czas_zakonczenia activities.end_time%type)
    LANGUAGE plpgsql
AS
$$
DECLARE
    warunek1 boolean;
    warunek2 boolean;
    warunek3 boolean;
BEGIN
    warunek1 = zajecia_grupy_w_danym_czasie(grupa_id, czas_rozpoczecia, czas_zakonczenia);
    warunek2 = zajecia_wykladowcy_w_danym_czasie(wykladowca_id, czas_rozpoczecia, czas_zakonczenia);
    warunek3 = wolna_sala(sala, czas_rozpoczecia, czas_zakonczenia);
    IF warunek1 = TRUE AND warunek2 = TRUE AND warunek3 = TRUE
    THEN
        INSERT INTO activities (start_time, end_time, room, unit_group)
        VALUES (czas_rozpoczecia, czas_zakonczenia, sala, grupa_id);
        RAISE NOTICE 'Dodano nowe zajecia';
    END IF;
    IF warunek1 = FALSE
    THEN
        RAISE NOTICE 'Nie można dodać nowych zajec, poniewaz w danym czasie grupa ma inne zajecia.';
    END IF;
    IF warunek2 = FALSE
    THEN
        RAISE NOTICE 'Nie można dodać nowych zajec, poniewaz w danym czasie wykładowca ma inne zajecia.';
    END IF;
    IF warunek3 = FALSE
    THEN
        RAISE NOTICE 'Nie można dodać nowych zajec, poniewaz w danym czasie sala jest zajeta.';
    END IF;
END;
$$;
CALL dodaj_nowe_zajecia(6, 8176, 'L-27.109', '2022-11-22 07:45:00.000000 +00:00', '2022-11-22 09:15:00.000000 +00:00');
--3 Przeniesc zajecia w czasie
CREATE OR REPLACE PROCEDURE przenieś_zajecia_w_czasie(id_zajec activities.activity_id%TYPE,
                                                      nowy_czas_rozpoczecia activities.start_time%TYPE,
                                                      nowy_czas_zakonczenia activities.end_time%TYPE)
    LANGUAGE plpgsql
AS
$$
DECLARE
    grupa_id      integer;
    wykladowca_id integer;
    sala          text;
    warunek1      boolean;
    warunek2      boolean;
    warunek3      boolean;
BEGIN
    SELECT unit_group_id, gt.teacher, r.room_id
    INTO grupa_id, wykladowca_id, sala
    FROM unit_groups ug
             INNER JOIN activities a ON ug.unit_group_id = a.unit_group
             INNER JOIN group_teacher gt ON ug.unit_group_id = gt.unit_group
             INNER JOIN rooms r ON r.room_id = a.room
    WHERE activity_id = id_zajec;

    warunek1 = zajecia_grupy_w_danym_czasie(grupa_id, nowy_czas_rozpoczecia, nowy_czas_zakonczenia);
    warunek2 = zajecia_wykladowcy_w_danym_czasie(wykladowca_id, nowy_czas_rozpoczecia, nowy_czas_zakonczenia);
    warunek3 = wolna_sala(sala, nowy_czas_rozpoczecia, nowy_czas_zakonczenia);
    IF warunek1 = TRUE AND warunek2 = TRUE AND warunek3 = TRUE
    THEN
        UPDATE activities
        SET start_time = nowy_czas_rozpoczecia,
            end_time   = nowy_czas_zakonczenia
        WHERE activity_id = id_zajec;
        RAISE NOTICE 'Przeniesiono zajecia na inną godzinę.';
    END IF;
    IF warunek1 = FALSE
    THEN
        RAISE NOTICE 'Nie mozna przeniesc zajec, poniewaz w danym czasie grupa ma inne zajecia.';
    END IF;
    IF warunek2 = FALSE
    THEN
        RAISE NOTICE 'Nie mozna przeniesc zajec, poniewaz w danym czasie wykładowca ma inne zajecia.';
    END IF;
    IF warunek3 = FALSE
    THEN
        RAISE NOTICE 'Nie mozna przeniesc zajec, poniewaz w danym czasie sala jest zajeta.';
    END IF;
END;
$$;
--4 Przenieść studenta do innej grupy
CREATE OR REPLACE PROCEDURE przenies_studenta_do_innej_grupy_na_jedne_zajecia(student_id users.usos_id%TYPE,
                                                                              obecna_grupa_id unit_groups.unit_group_id%TYPE,
                                                                              nowa_grupa_id unit_groups.unit_group_id%TYPE)
    LANGUAGE plpgsql
AS
$$
DECLARE
    sala                 text;
    student_nie_ma_zajec bool = TRUE;
    x                    record;
BEGIN
    SELECT room_id
    INTO sala
    FROM rooms
             INNER JOIN activities a ON rooms.room_id = a.room
             INNER JOIN unit_groups ug ON ug.unit_group_id = a.unit_group
    WHERE unit_group_id = nowa_grupa_id;

    FOR x IN SELECT start_time, end_time
             FROM activities a
                      INNER JOIN unit_groups u ON u.unit_group_id = a.unit_group
             WHERE unit_group_id = nowa_grupa_id
        LOOP
            IF zajecia_studenta_w_danym_czasie(student_id, x.start_time, x.end_time) = FALSE
            THEN
                student_nie_ma_zajec = FALSE;
            END IF;
        END LOOP;
    IF student_nie_ma_zajec
    THEN
        UPDATE users_groups
        SET group_id = nowa_grupa_id
        WHERE user_usos_id = student_id
          AND group_id = obecna_grupa_id;
    ELSE
        RAISE NOTICE 'Student nie moze zmienic grupy';
    END IF;
END;
$$;
--5 Przenieś studenta do innej grupy na wszystkie zajecia
CREATE OR REPLACE PROCEDURE przenies_studenta_na_wszystkie_zajecia(id_studenta users.usos_id%TYPE,
                                                                   rodzaj_zajec group_types.group_type_id%TYPE,
                                                                   nr_nowej_grupy unit_groups.group_number%TYPE)
    LANGUAGE plpgsql
AS
$$
DECLARE
    x              record;
    nie_ma_zajec   boolean = TRUE;
    y              record;
    id_nowej_grupy unit_groups.unit_group_id%TYPE;
BEGIN
    DROP TABLE IF EXISTS temp_przenosiny;
    CREATE TEMP TABLE temp_przenosiny AS
    SELECT unit_groups.usos_unit_id, unit_groups.group_number, unit_groups.unit_group_id
    FROM unit_groups
             INNER JOIN users_groups ug ON unit_groups.unit_group_id = ug.group_id
             INNER JOIN usos_units uu ON uu.usos_unit_id = unit_groups.usos_unit_id
             INNER JOIN users u ON u.usos_id = ug.user_usos_id
    WHERE id_studenta = u.usos_id
      AND uu.group_type = rodzaj_zajec;
    FOR x IN SELECT * FROM temp_przenosiny
        LOOP
            FOR y IN SELECT a.start_time,
                            a.end_time
                     FROM activities a
                              INNER JOIN unit_groups u ON u.unit_group_id = a.unit_group
                     WHERE u.usos_unit_id = x.usos_unit_id
                       AND u.group_number = nr_nowej_grupy
                LOOP
                    IF
                            zajecia_studenta_w_danym_czasie(id_studenta, y.start_time, y.end_time, x.usos_unit_id) =
                            FALSE
                    THEN
                        nie_ma_zajec = FALSE;
                    END IF;
                END LOOP;
        END LOOP;
    IF nie_ma_zajec
    THEN
        FOR x IN SELECT * FROM temp_przenosiny
            LOOP
                SELECT unit_group_id
                INTO id_nowej_grupy
                FROM unit_groups
                WHERE usos_unit_id = x.usos_unit_id
                  AND group_number = nr_nowej_grupy;
                UPDATE users_groups
                SET group_id = id_nowej_grupy
                WHERE user_usos_id = id_studenta
                  AND group_id = x.unit_group_id;
            END LOOP;
        RAISE NOTICE 'Nie zajec true';
    ELSE
        RAISE NOTICE 'False';
    END IF;
END;

$$;
CALL przenies_studenta_na_wszystkie_zajecia(234394, 'LEK', 1);
SELECT group_number
FROM unit_groups
         INNER JOIN users_groups ug ON unit_groups.unit_group_id = ug.group_id
         INNER JOIN users u ON u.usos_id = ug.user_usos_id
WHERE u.usos_id = 233921;

SELECT unit_groups.usos_unit_id, group_number
FROM unit_groups
         INNER JOIN users_groups ug ON unit_groups.unit_group_id = ug.group_id
         INNER JOIN usos_units uu ON uu.usos_unit_id = unit_groups.usos_unit_id
         INNER JOIN users u ON u.usos_id = ug.user_usos_id
WHERE 233921 = u.usos_id
  AND uu.group_type = 'WYK';