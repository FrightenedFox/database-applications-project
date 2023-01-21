-- 1
CREATE OR REPLACE FUNCTION grupa_ma_wolne_miejsca(id_grupy unit_groups.unit_group_id%TYPE)
    RETURNS BOOLEAN
    LANGUAGE plpgsql
AS
$$
DECLARE
    liczebnosc_grupy INTEGER;
    min_rozmiar_sali public.rooms.capacity%TYPE;
BEGIN
    liczebnosc_grupy = ilosc_studentow_w_grupie(id_grupy);
    SELECT MIN(r.capacity)
    INTO min_rozmiar_sali
    FROM unit_groups ung
             INNER JOIN activities a ON ung.unit_group_id = a.unit_group
             INNER JOIN rooms r ON r.room_id = a.room
    WHERE ung.unit_group_id = id_grupy;

    CASE
        WHEN min_rozmiar_sali < liczebnosc_grupy
            THEN RAISE DATA_EXCEPTION USING MESSAGE = 'Grupa już nie mieści się w niektórych salach!';
        WHEN min_rozmiar_sali = liczebnosc_grupy THEN RETURN FALSE;
        ELSE RETURN TRUE;
        END CASE;
END
$$;
-- SELECT grupa_ma_wolne_miejsca(18);


-- 2
-- Wersja pierwsza
CREATE OR REPLACE FUNCTION zajecia_studenta_w_danym_czasie(
    student users.usos_id%TYPE,
    czas_poczatkowy activities.start_time%TYPE,
    czas_koncowy activities.end_time%TYPE
)
    RETURNS bool
    LANGUAGE plpgsql
AS
$$
DECLARE
    liczba_kolidujacych_zajec INT;
BEGIN
    SELECT COUNT(activity_id)
    INTO liczba_kolidujacych_zajec
    FROM activities act
             INNER JOIN unit_groups ung ON act.unit_group = ung.unit_group_id
             INNER JOIN users_groups usg ON ung.unit_group_id = usg.group_id
             INNER JOIN users u ON u.usos_id = usg.user_usos_id
    WHERE (start_time >= czas_poczatkowy AND start_time < czas_koncowy
        OR end_time > czas_poczatkowy AND end_time <= czas_koncowy)
      AND u.usos_id = student;

    IF liczba_kolidujacych_zajec > 0 THEN
        RETURN FALSE;
    ELSIF liczba_kolidujacych_zajec = 0 THEN
        RETURN TRUE;
    END IF;
END;
$$;

-- Wersja druga
CREATE OR REPLACE FUNCTION zajecia_studenta_w_danym_czasie(
    student users.usos_id%TYPE,
    czas_poczatkowy activities.start_time%TYPE,
    czas_koncowy activities.end_time%TYPE,
    ignoruj_usos_unit_id usos_units.usos_unit_id%TYPE
)
    RETURNS bool
    LANGUAGE plpgsql
AS
$$
DECLARE
    liczba_kolidujacych_zajec INT;
BEGIN
    SELECT COUNT(activity_id)
    INTO liczba_kolidujacych_zajec
    FROM activities act
             INNER JOIN unit_groups ung ON act.unit_group = ung.unit_group_id
             INNER JOIN users_groups usg ON ung.unit_group_id = usg.group_id
             INNER JOIN users u ON u.usos_id = usg.user_usos_id
    WHERE (start_time >= czas_poczatkowy AND start_time < czas_koncowy
        OR end_time > czas_poczatkowy AND end_time <= czas_koncowy)
      AND u.usos_id = student
      AND ung.usos_unit_id != ignoruj_usos_unit_id;

    IF liczba_kolidujacych_zajec > 0 THEN
        RETURN FALSE;
    ELSIF liczba_kolidujacych_zajec = 0 THEN
        RETURN TRUE;
    END IF;
END;
$$;

-- Wersja trzecia
CREATE OR REPLACE FUNCTION zajecia_studenta_w_danym_czasie(
    student users.usos_id%TYPE,
    czas_poczatkowy activities.start_time%TYPE,
    czas_koncowy activities.end_time%TYPE,
    ignoruj_liste_usos_unit_ids INTEGER ARRAY
)
    RETURNS bool
    LANGUAGE plpgsql
AS
$$
DECLARE
    liczba_kolidujacych_zajec INT;
BEGIN
    SELECT COUNT(activity_id)
    INTO liczba_kolidujacych_zajec
    FROM activities act
             INNER JOIN unit_groups ung ON act.unit_group = ung.unit_group_id
             INNER JOIN users_groups usg ON ung.unit_group_id = usg.group_id
             INNER JOIN users u ON u.usos_id = usg.user_usos_id
    WHERE (start_time >= czas_poczatkowy AND start_time < czas_koncowy
        OR end_time > czas_poczatkowy AND end_time <= czas_koncowy)
      AND u.usos_id = student
      AND ung.usos_unit_id != ALL (ignoruj_liste_usos_unit_ids);

    IF liczba_kolidujacych_zajec > 0 THEN
        RETURN FALSE;
    ELSIF liczba_kolidujacych_zajec = 0 THEN
        RETURN TRUE;
    END IF;
END;
$$;

-- SELECT zajecia_studenta_w_danym_czasie(234394, TIMESTAMP '2022-12-16 16:46:00', TIMESTAMP '2022-12-16 17:30:00');


-- 3
CREATE OR REPLACE FUNCTION zajecia_wykladowcy_w_danym_czasie(wykladowca teachers.teacher_usos_id%TYPE,
                                                             czas_poczatkowy activities.start_time%TYPE,
                                                             czas_koncowy activities.end_time%TYPE)
    RETURNS bool
    LANGUAGE plpgsql
AS
$$
DECLARE
    wynik INT;
BEGIN
    SELECT COUNT(activity_id)
    INTO wynik
    FROM activities act
             INNER JOIN unit_groups ug ON ug.unit_group_id = act.unit_group
             INNER JOIN group_teacher gt ON ug.unit_group_id = gt.unit_group
             INNER JOIN teachers t ON t.teacher_usos_id = gt.teacher
    WHERE (start_time >= czas_poczatkowy AND start_time < czas_koncowy
        OR end_time > czas_poczatkowy AND end_time <= czas_koncowy)
      AND t.teacher_usos_id = wykladowca;
    IF wynik > 0 THEN
        RETURN FALSE;
    ELSIF wynik = 0 THEN
        RETURN TRUE;
    END IF;
END;
$$;
-- SELECT zajecia_wykladowcy_w_danym_czasie(8640, TIMESTAMP '2022-12-16 09:25:00', TIMESTAMP '2022-12-16 10:00:00');


--4
CREATE OR REPLACE FUNCTION zajecia_grupy_w_danym_czasie(grupa unit_groups.unit_group_id%TYPE,
                                                        czas_poczatkowy activities.start_time%TYPE,
                                                        czas_koncowy activities.end_time%TYPE)
    RETURNS bool
    LANGUAGE plpgsql
AS
$$
DECLARE
    wynik INT;
BEGIN
    SELECT COUNT(activity_id)
    INTO wynik
    FROM activities act
             INNER JOIN unit_groups ug ON ug.unit_group_id = act.unit_group
    WHERE (start_time >= czas_poczatkowy AND start_time < czas_koncowy
        OR end_time > czas_poczatkowy AND end_time <= czas_koncowy)
      AND ug.unit_group_id = grupa;
    IF wynik > 0 THEN
        RETURN FALSE;
    ELSIF wynik = 0 THEN
        RETURN TRUE;
    END IF;
END;
$$;
-- SELECT zajecia_grupy_w_danym_czasie(23, TIMESTAMP '2022-12-16 15:25:00', TIMESTAMP '2022-12-16 16:00:00');


--5
CREATE OR REPLACE FUNCTION wolna_sala(sala rooms.room_id%TYPE,
                                      czas_poczatkowy activities.start_time%TYPE,
                                      czas_koncowy activities.end_time%TYPE)
    RETURNS bool
    LANGUAGE plpgsql
AS
$$
DECLARE
    wynik INT;
BEGIN
    SELECT COUNT(activity_id)
    INTO wynik
    FROM activities act
             INNER JOIN rooms r ON r.room_id = act.room
    WHERE (start_time >= czas_poczatkowy AND start_time < czas_koncowy
        OR end_time > czas_poczatkowy AND end_time <= czas_koncowy)
      AND r.room_id = sala;
    IF wynik > 0 THEN
        RETURN FALSE;
    ELSIF wynik = 0 THEN
        RETURN TRUE;
    END IF;
END;
$$;
-- SELECT wolna_sala('P.15(P-2.401)', TIMESTAMP '2022-12-16 09:25:00', TIMESTAMP '2022-12-16 10:00:00');


-- 6
CREATE OR REPLACE FUNCTION ilosc_godzin_wykladowcy(wykladowca teachers.teacher_usos_id%TYPE) RETURNS DOUBLE PRECISION AS
$$
DECLARE
    zajecie     RECORD;
    grupa       INT;
    laczny_czas DOUBLE PRECISION := 0.0;
BEGIN
    FOR grupa IN SELECT unit_group
                 FROM group_teacher
                 WHERE teacher = wykladowca
        LOOP
            FOR zajecie IN SELECT start_time, end_time
                           FROM activities
                           WHERE unit_group = grupa
                LOOP
                    laczny_czas := laczny_czas +
                                   EXTRACT(EPOCH FROM AGE(zajecie.end_time, zajecie.start_time))
                                       / 3600 AS difference;
                END LOOP;
        END LOOP;
    RETURN laczny_czas;
END;
$$ LANGUAGE plpgsql;
-- SELECT ilosc_godzin_wykladowcy(186812);


--7
CREATE OR REPLACE FUNCTION ilosc_godzin_studenta(student users.usos_id%TYPE) RETURNS DOUBLE PRECISION AS
$$
DECLARE
    zajecie     RECORD;
    grupa       INT;
    laczny_czas DOUBLE PRECISION := 0.0;
BEGIN
    FOR grupa IN SELECT group_id FROM users_groups WHERE user_usos_id = student
        LOOP
            FOR zajecie IN SELECT start_time, end_time FROM activities WHERE unit_group = grupa
                LOOP
                    laczny_czas := laczny_czas +
                                   EXTRACT(EPOCH FROM AGE(zajecie.end_time, zajecie.start_time)) / 3600 AS difference;
                END LOOP;
        END LOOP;
    RETURN laczny_czas;
END;
$$ LANGUAGE plpgsql;
-- SELECT ilosc_godzin_studenta(234394);


-- 8
CREATE OR REPLACE FUNCTION odleglosc_miedzy_budynkami(budynek_a_id buildings.building_id%TYPE,
                                                      budynek_b_id buildings.building_id%TYPE)
    RETURNS DOUBLE PRECISION
    LANGUAGE plpgsql
AS
$$
DECLARE
    odleglosc   DOUBLE PRECISION;
    dlugosc_a   DOUBLE PRECISION;
    szerokosc_a DOUBLE PRECISION;
    budynek_b   buildings%ROWTYPE;
BEGIN
    SELECT RADIANS(bud.longitude), RADIANS(bud.latitude)
    INTO dlugosc_a, szerokosc_a
    FROM buildings bud
    WHERE building_id = budynek_a_id;
    SELECT bud.building_id, bud.building_name, RADIANS(bud.longitude), RADIANS(bud.latitude)
    INTO budynek_b
    FROM buildings bud
    WHERE building_id = budynek_b_id;
    odleglosc = 2 * 6371000 * ASIN(SQRT(SIN((budynek_b.longitude - dlugosc_a) / 2) ^ 2 +
                                        COS(dlugosc_a) * COS(budynek_b.longitude) *
                                        SIN((budynek_b.latitude - szerokosc_a) / 2) ^ 2));

    RETURN odleglosc;
END;
$$;
-- SELECT odleglosc_miedzy_budynkami('F', 'P');


-- 9
CREATE OR REPLACE FUNCTION ilosc_studentow_w_grupie(IN id_grupy public.unit_groups.unit_group_id%TYPE)
    RETURNS INTEGER
    LANGUAGE plpgsql
AS
$$
DECLARE
    liczebnosc_grupy INTEGER;
BEGIN
    SELECT COUNT(DISTINCT usg.user_usos_id)
    INTO liczebnosc_grupy
    FROM public.unit_groups ung
             INNER JOIN users_groups usg ON ung.unit_group_id = usg.group_id
    WHERE ung.unit_group_id = id_grupy;
    RETURN liczebnosc_grupy;
END;
$$;



-- 10
CREATE OR REPLACE FUNCTION grupa_z_min_iloscia_studentow(IN typ_grupy public.group_types.group_type_id%TYPE)
    RETURNS DOUBLE PRECISION
    LANGUAGE plpgsql
AS
$$
DECLARE
    najmniej_liczebna_grupa RECORD;
BEGIN
    SELECT ung.group_number numer_grupy, AVG(ilosc_studentow_w_grupie(ung.unit_group_id)) srednia_ilosc_studentow
    INTO najmniej_liczebna_grupa
    FROM unit_groups ung
             INNER JOIN (SELECT DISTINCT uu.usos_unit_id, uu.group_type
                         FROM usos_units uu
                                  INNER JOIN unit_groups ung2 ON uu.usos_unit_id = ung2.usos_unit_id
                                  INNER JOIN users_groups usg ON ung2.unit_group_id = usg.group_id
                              -- Nie jest to błąd, po prostu ograniczamy się do 3 roku IiAD,
                              -- podany user_usos_id to ID Vitalii'a Morskyiego
                         WHERE usg.user_usos_id = 234394) y3uu ON ung.usos_unit_id = y3uu.usos_unit_id
    WHERE y3uu.group_type = typ_grupy
    GROUP BY ung.group_number
    ORDER BY srednia_ilosc_studentow, numer_grupy
    LIMIT 1;
    RETURN najmniej_liczebna_grupa.numer_grupy;
END;
$$;

-- SELECT grupa_z_min_iloscia_studentow('LAB');
