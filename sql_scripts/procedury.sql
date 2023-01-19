--1 Zmiana prowadzacego
CREATE OR REPLACE PROCEDURE zmien_prowadzacego(IN grupa_id unit_groups.unit_group_id%TYPE,
                                               IN wykladowca_id group_teacher.teacher%TYPE,
                                               OUT result TEXT)
    LANGUAGE plpgsql
AS
$$
DECLARE
    poczatek TIMESTAMP;
    koniec   TIMESTAMP;
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
        result = 'Wykładowca został zmieniony.';
    ELSE
        RAISE EXCEPTION 'Wykładowca nie został zmieniony, ponieważ ma wtedy zajęcia.';
    END IF;
END
$$;
-- -- CALL zmien_prowadzacego(18, 27061);
--2 Dodanie nowych zajec
CREATE OR REPLACE PROCEDURE dodaj_nowe_zajecia(grupa_id unit_groups.unit_group_id%TYPE,
                                               sala rooms.room_id%TYPE,
                                               czas_rozpoczecia activities.start_time%TYPE,
                                               czas_zakonczenia activities.end_time%TYPE,
                                               OUT result TEXT)
    LANGUAGE plpgsql
AS
$$
DECLARE
    wykladowca_id group_teacher.teacher%TYPE;
    warunek1      BOOLEAN;
    warunek2      BOOLEAN;
    warunek3      BOOLEAN;
BEGIN
    -- TODO: dodać warunek, który sprawdza czy czas rozpoczęcia jest mniejszy (wcześniejszy) od czasu zakończenia.
    SELECT t.teacher_usos_id
    INTO wykladowca_id
    FROM teachers t
             INNER JOIN group_teacher gt ON t.teacher_usos_id = gt.teacher
             INNER JOIN unit_groups ug ON ug.unit_group_id = gt.unit_group
    WHERE ug.unit_group_id = grupa_id;
    warunek1 = zajecia_grupy_w_danym_czasie(grupa_id, czas_rozpoczecia, czas_zakonczenia);
    warunek2 = zajecia_wykladowcy_w_danym_czasie(wykladowca_id, czas_rozpoczecia, czas_zakonczenia);
    warunek3 = wolna_sala(sala, czas_rozpoczecia, czas_zakonczenia);
    IF warunek1 = TRUE AND warunek2 = TRUE AND warunek3 = TRUE
    THEN
        INSERT INTO activities (start_time, end_time, room, unit_group)
        VALUES (czas_rozpoczecia, czas_zakonczenia, sala, grupa_id);
        result = 'Dodano nowe zajęcia.';
    END IF;
    IF warunek1 = FALSE
    THEN
        RAISE EXCEPTION 'Nie można dodać nowych zajec, poniewaz w danym czasie grupa ma inne zajecia.';
    END IF;
    IF warunek2 = FALSE
    THEN
        RAISE EXCEPTION 'Nie można dodać nowych zajec, poniewaz w danym czasie wykładowca ma inne zajecia.';
    END IF;
    IF warunek3 = FALSE
    THEN
        RAISE EXCEPTION 'Nie można dodać nowych zajec, poniewaz w danym czasie sala jest zajeta.';
    END IF;
END;
$$;
-- -- CALL dodaj_nowe_zajecia(6, 8176, 'L-27.109', '2022-11-22 07:45:00.000000 +00:00', '2022-11-22 09:15:00.000000 +00:00');
--3 Przeniesc zajecia w czasie
CREATE OR REPLACE PROCEDURE przenieś_zajecia_w_czasie(id_zajec activities.activity_id%TYPE,
                                                      nowy_czas_rozpoczecia activities.start_time%TYPE,
                                                      nowy_czas_zakonczenia activities.end_time%TYPE,
                                                      OUT result TEXT)
    LANGUAGE plpgsql
AS
$$
DECLARE
    grupa_id      INTEGER;
    wykladowca_id INTEGER;
    sala          TEXT;
    warunek1      BOOLEAN;
    warunek2      BOOLEAN;
    warunek3      BOOLEAN;
BEGIN
    -- TODO: dodać warunek, który sprawdza czy czas rozpoczęcia jest mniejszy (wcześniejszy) od czasu zakończenia.
    SELECT unit_group_id, gt.teacher, r.room_id
    INTO grupa_id, wykladowca_id, sala
    FROM unit_groups ug
             INNER JOIN activities a ON ug.unit_group_id = a.unit_group
             INNER JOIN group_teacher gt ON ug.unit_group_id = gt.unit_group
             INNER JOIN rooms r ON r.room_id = a.room
    WHERE activity_id = id_zajec;

    -- TODO: w tej chwili procedura nie pozwala przenieść zajęcia na inny czas, jeżeli przenosimy ich w taki sposób,
    --  że nakładają się "sami na siebie". Np jeżeli przenosimy zajęcia z godziny 10:30-12:00 na godzinę 11:00-12:30
    --  (godziny nakładają się), to procedura widzi następną sytuację:
    --      a) grupa ma zajęcia w tym czasie (ma, ale je przenosimy, więc już nie ma tych zajęć);
    --      b) wykładowca ma zajęcia (analogicznie);
    --      c) sala jest zajęta (analogicznie).
    --  Trzeba to poprawić w taki sposób, żeby procedura nie brała pod uwagę tych zajęć, które przenosimy.
    --  Sprytnie to z tobą rozwiązaliśmy w funkcji `zajecia_studenta_w_danym_czasie`: dodaliśmy tam parametr
    --  `ignoruj_usos_unit_id` i funkcja nie bierze pod uwagę zajęcia studenta w tej grupie (usos_unit_id).
    --  Proponuję analogicznie to rozwiązać w następnych funkcjach:
    --      1) zajecia_grupy_w_danym_czasie
    --      2) zajecia_wykladowcy_w_danym_czasie
    --      3) wolna_sala
    --  Na koniec trzeba będzie zmodyfikować wyłowanie poniższych warunków tak, aby uwzględniać ten numer grupy.

    warunek1 = zajecia_grupy_w_danym_czasie(grupa_id, nowy_czas_rozpoczecia, nowy_czas_zakonczenia);
    warunek2 = zajecia_wykladowcy_w_danym_czasie(wykladowca_id, nowy_czas_rozpoczecia, nowy_czas_zakonczenia);
    warunek3 = wolna_sala(sala, nowy_czas_rozpoczecia, nowy_czas_zakonczenia);
    IF warunek1 = TRUE AND warunek2 = TRUE AND warunek3 = TRUE
    THEN
        UPDATE activities
        SET start_time = nowy_czas_rozpoczecia,
            end_time   = nowy_czas_zakonczenia
        WHERE activity_id = id_zajec;
        result = 'Przeniesiono zajęcia na wskazany czas.';
    END IF;
    IF warunek1 = FALSE
    THEN
        RAISE EXCEPTION 'Nie mozna przeniesc zajec, poniewaz w danym czasie grupa ma inne zajecia.';
    END IF;
    IF warunek2 = FALSE
    THEN
        RAISE EXCEPTION 'Nie mozna przeniesc zajec, poniewaz w danym czasie wykładowca ma inne zajecia.';
    END IF;
    IF warunek3 = FALSE
    THEN
        RAISE EXCEPTION 'Nie mozna przeniesc zajec, poniewaz w danym czasie sala jest zajeta.';
    END IF;
END;
$$;
--4 Przenieść studenta do innej grupy
CREATE OR REPLACE PROCEDURE przenies_studenta_do_innej_grupy_na_jedne_zajecia(student_id users.usos_id%TYPE,
                                                                              obecna_grupa_id unit_groups.unit_group_id%TYPE,
                                                                              nowa_grupa_id unit_groups.unit_group_id%TYPE,
                                                                              OUT result TEXT)
    LANGUAGE plpgsql
AS
$$
DECLARE
    sala                 TEXT;
    student_nie_ma_zajec bool = TRUE;
    x                    RECORD;
BEGIN
    SELECT room_id
    INTO sala
    FROM rooms
             INNER JOIN activities a ON rooms.room_id = a.room
             INNER JOIN unit_groups ug ON ug.unit_group_id = a.unit_group
    WHERE unit_group_id = nowa_grupa_id;
    --  TODO: sprawdzić czy w grupie jest wolne miejsce dla studenta (w tym celu stworzyć osobną funkcję, ponieważ
    --   analogiczny warunek jest wykorzystywany w procedurze `przenies_studenta_na_wszystkie_zajecia`).
    FOR x IN SELECT start_time, end_time
             FROM activities a
                      INNER JOIN unit_groups u ON u.unit_group_id = a.unit_group
             WHERE unit_group_id = nowa_grupa_id
        LOOP
            IF zajecia_studenta_w_danym_czasie(student_id, x.start_time, x.end_time, obecna_grupa_id) = FALSE
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
        result = 'Student został przepisany do innej grupy.';
    ELSE
        RAISE EXCEPTION 'Student nie może zmienić grupy, ponieważ w wybranym czasie on ma inne zajęcia.';
    END IF;
END;
$$;
--5 Przenieś studenta do innej grupy na wszystkie zajecia
CREATE OR REPLACE PROCEDURE przenies_studenta_na_wszystkie_zajecia(id_studenta users.usos_id%TYPE,
                                                                   rodzaj_zajec group_types.group_type_id%TYPE,
                                                                   nr_nowej_grupy unit_groups.group_number%TYPE,
                                                                   OUT result TEXT)
    LANGUAGE plpgsql
AS
$$
DECLARE
    single_group_to_move           RECORD;
    nie_ma_zajec                   BOOLEAN = TRUE;
    activities_of_the_moving_group RECORD;
    id_nowej_grupy                 unit_groups.unit_group_id%TYPE;
    lista_grup_studenta            INTEGER ARRAY;
BEGIN
    CREATE TEMP TABLE unit_groups_to_move AS
    SELECT unit_groups.usos_unit_id, unit_groups.group_number, unit_groups.unit_group_id
    FROM unit_groups
             INNER JOIN users_groups ug ON unit_groups.unit_group_id = ug.group_id
             INNER JOIN usos_units uu ON uu.usos_unit_id = unit_groups.usos_unit_id
             INNER JOIN users u ON u.usos_id = ug.user_usos_id
    WHERE id_studenta = u.usos_id
      AND uu.group_type = rodzaj_zajec;
    SELECT INTO lista_grup_studenta ARRAY(SELECT usos_unit_id FROM unit_groups_to_move);
    FOR single_group_to_move IN SELECT * FROM unit_groups_to_move
        LOOP
            FOR activities_of_the_moving_group IN
                SELECT a.start_time,
                       a.end_time
                FROM activities a
                         INNER JOIN unit_groups u ON u.unit_group_id = a.unit_group
                WHERE u.usos_unit_id = single_group_to_move.usos_unit_id
                  AND u.group_number = nr_nowej_grupy
                LOOP
                    IF
                            zajecia_studenta_w_danym_czasie(
                                    id_studenta,
                                    activities_of_the_moving_group.start_time,
                                    activities_of_the_moving_group.end_time,
                                    lista_grup_studenta) = FALSE
                    THEN
                        nie_ma_zajec = FALSE;
                    END IF;
                END LOOP;
        END LOOP;
    --  TODO: sprawdzić czy w grupie jest wolne miejsce dla studenta (w tym celu stworzyć osobną funkcję, ponieważ
    --   analogiczny warunek jest wykorzystywany w procedurze `przenies_studenta_do_innej_grupy_na_jedne_zajecia`).
    IF nie_ma_zajec
    THEN
        FOR single_group_to_move IN SELECT * FROM unit_groups_to_move
            LOOP
                SELECT unit_group_id
                INTO id_nowej_grupy
                FROM unit_groups
                WHERE usos_unit_id = single_group_to_move.usos_unit_id
                  AND group_number = nr_nowej_grupy;
                UPDATE users_groups
                SET group_id = id_nowej_grupy
                WHERE user_usos_id = id_studenta
                  AND group_id = single_group_to_move.unit_group_id;
            END LOOP;
        result = 'Student został przeniesiony do nowej grupy.';
    ELSE
        RAISE EXCEPTION 'Student nie został przeniesiony do nowej grupy';
    END IF;
    DROP TABLE IF EXISTS unit_groups_to_move;
END;

$$;
-- CALL przenies_studenta_na_wszystkie_zajecia(234394, 'LAB', 6, '???', TRUE);
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


SELECT PG_GET_SERIAL_SEQUENCE('teachers', 'teacher_usos_id');
CREATE SEQUENCE IF NOT EXISTS teachers_custom_usos_id_seq
    AS INTEGER INCREMENT BY 1 START WITH 1 OWNED BY public.teachers.teacher_usos_id;

CREATE OR REPLACE PROCEDURE dodaj_nowego_prowadzacego(
    IN imie public.teachers.first_name%TYPE,
    IN nazwisko public.teachers.last_name%TYPE,
    OUT result TEXT
)
    LANGUAGE plpgsql
AS

$$
BEGIN
    CASE
        WHEN imie !~ '^[A-Z][a-z]+$'
            THEN RAISE EXCEPTION 'Imię powinno zawierać tylko znaki ASCII, pierwsza litera powinna być duża.';
        WHEN nazwisko !~ '^[A-Z][a-z]+$'
            THEN RAISE EXCEPTION 'Nazwisko powinno zawierać tylko znaki ASCII, pierwsza litera powinna być duża.';
        WHEN (SELECT COUNT(t.teacher_usos_id) FROM teachers t WHERE t.first_name = imie AND t.last_name = nazwisko) > 0
            THEN RAISE EXCEPTION 'Nowy prowadzący nie został dodany, ponieważ podane dane prowadzącego już znajdują się w bazie.';
        ELSE INSERT INTO public.teachers (teacher_usos_id, first_name, last_name)
             VALUES (NEXTVAL('public.teachers_custom_usos_id_seq'), imie, nazwisko);
             result = 'Nowy prowadzący został pomyślnie dodany do bazy.';
        END CASE;
END;
$$;

CREATE OR REPLACE PROCEDURE dodaj_nowy_budynek(
    IN id_budynku public.buildings.building_id%TYPE,
    IN nazwa_budynku public.buildings.building_name%TYPE,
    IN dlugosc_geo public.buildings.longitude%TYPE,
    IN szerokosc_geo public.buildings.latitude%TYPE,
    OUT result TEXT
)
    LANGUAGE plpgsql
AS

$$
BEGIN
    CASE
        WHEN (SELECT COUNT(b.building_id)
              FROM buildings b
              WHERE b.building_id = id_budynku
                 OR b.building_name = nazwa_budynku) > 0
            THEN RAISE EXCEPTION 'Nowy budynek nie został dodany, ponieważ podana nazwa lub id budynku już znajduje się w bazie.';
        WHEN NOT (
            (dlugosc_geo > 21.903 AND dlugosc_geo < 22.080 AND szerokosc_geo > 49.977 AND szerokosc_geo < 50.136)
            OR
            (dlugosc_geo > 22.003 AND dlugosc_geo < 22.150 AND szerokosc_geo > 50.486 AND szerokosc_geo < 50.665)
            ) then RAISE EXCEPTION 'Budynek nie został dodany, ponieważ podane współrzędne geograficzne nie znajdują się w Rzeszowie lub Stalowej Woli.';
        ELSE INSERT INTO public.buildings (building_id, building_name, longitude, latitude)
             VALUES (id_budynku, nazwa_budynku, dlugosc_geo, szerokosc_geo);
             result = 'Nowy budynek został pomyślnie dodany do bazy.';
        END CASE;
END;
$$;

-- Graniczne współrzędne Rzeszowa
-- 50.035191, 21.903421
-- 50.027440, 22.080943
-- 50.136168, 22.001790
-- 49.977605, 21.991233
-- Graniczne współrzędne Stalowej Woli
-- 50.576391, 22.003445
-- 50.582724, 22.150546
-- 50.665115, 22.036575
-- 50.485998, 22.067751

SELECT PG_GET_SERIAL_SEQUENCE('users', 'usos_id');
CREATE SEQUENCE IF NOT EXISTS users_custom_usos_id_seq
    AS INTEGER INCREMENT BY 1 START WITH 1 OWNED BY public.users.usos_id;

CREATE OR REPLACE PROCEDURE auto_dodaj_studenta(
    IN imie public.users.first_name%TYPE,
    IN nazwisko public.users.last_name%TYPE,
    OUT result TEXT
)
    LANGUAGE plpgsql
AS
$$
DECLARE
    new_user_usos_id   public.users.usos_id%TYPE;
    gr_lek             public.unit_groups.group_number%TYPE;
    gr_lab_pro         public.unit_groups.group_number%TYPE;
    gr_cw              public.unit_groups.group_number%TYPE;
    gr_wyk             public.unit_groups.group_number%TYPE;
    cur_usos_units CURSOR FOR SELECT usos_unit_id, group_type
                              FROM public.usos_units;
    single_usos_unit   RECORD;
    temp_unit_group_id public.unit_groups.unit_group_id%TYPE;
    temp_gr_number     public.unit_groups.group_number%TYPE;
BEGIN
    CASE
        WHEN imie !~ '^[A-Z][a-z]+$'
            THEN RAISE EXCEPTION 'Imię powinno zawierać tylko znaki ASCII, pierwsza litera powinna być duża.';
        WHEN nazwisko !~ '^[A-Z][a-z]+$'
            THEN RAISE EXCEPTION 'Nazwisko powinno zawierać tylko znaki ASCII, pierwsza litera powinna być duża.';
        ELSE BEGIN
            -- Dodajemy nowego studenta do bazy.
            new_user_usos_id = NEXTVAL('public.users_custom_usos_id_seq');
            INSERT INTO public.users (usos_id, first_name, last_name)
            VALUES (new_user_usos_id, imie, nazwisko);

            -- Poszukiwanie grup o najmniejszej ilości studentów
            gr_lek = grupa_z_min_iloscia_studentow('LEK');
            gr_lab_pro = grupa_z_min_iloscia_studentow('LAB');
            CASE gr_lab_pro
                WHEN 1, 2 THEN gr_cw = 1;
                WHEN 3, 4 THEN gr_cw = 2;
                WHEN 5, 6 THEN gr_cw = 3;
                ELSE RAISE EXCEPTION 'Lab/pro group (%) is unknown.', gr_lab_pro;
                END CASE;
            gr_wyk = grupa_z_min_iloscia_studentow('WYK');

            -- Dodawanie studenta do każdego typu grupy każdego przedmiotu
            OPEN cur_usos_units;
            LOOP
                FETCH cur_usos_units INTO single_usos_unit;
                EXIT WHEN NOT found;

                CASE single_usos_unit.group_type
                    WHEN 'WYK' THEN temp_gr_number = gr_wyk;
                    WHEN 'LAB', 'PRO' THEN temp_gr_number = gr_lab_pro;
                    WHEN 'ĆW' THEN temp_gr_number = gr_cw;
                    WHEN 'LEK' THEN temp_gr_number = gr_lek;
                    ELSE RAISE EXCEPTION 'Group type (%) is unknown.', single_usos_unit.group_type;
                    END CASE;

                SELECT ung.unit_group_id
                INTO temp_unit_group_id
                FROM public.unit_groups ung
                WHERE ung.group_number = temp_gr_number
                  AND ung.usos_unit_id = single_usos_unit.usos_unit_id;

                INSERT INTO public.users_groups (user_usos_id, group_id) VALUES (new_user_usos_id, temp_unit_group_id);
                result = FORMAT('Studnet został został dodany do grup WYK %s, ĆW %s, LAB-PRO %s i LEK %s.',
                                gr_wyk, gr_cw, gr_lab_pro, gr_lek);
            END LOOP;
            CLOSE cur_usos_units;

        END;
-- TODO: exceptions
        END CASE;
END;
$$;

CALL auto_dodaj_studenta('Paul', 'Massaro', '');

CREATE OR REPLACE FUNCTION test() RETURNS INTEGER[]
    LANGUAGE plpgsql
AS
$$
DECLARE
    a INTEGER ARRAY;
    b INTEGER;
BEGIN
    b = 2;
    a = ARRAY [2, 3, 4];
    a = '{12, 3, 4}';
    SELECT INTO a ARRAY(SELECT usos_unit_id FROM unit_groups);
    RETURN a;
END;
$$;

SELECT test
FROM test();

DROP FUNCTION test;

