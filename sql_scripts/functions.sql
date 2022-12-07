-- 1
CREATE OR REPLACE FUNCTION sprawdzanie_wolnego_miejsca(grupa_id IN unit_groups.unit_group_id%TYPE)
    RETURNS wynik
    LANGUAGE plpgsql
AS
$$
DECLARE
    ilosc_osob INTEGER wynik bool
BEGIN
    SELECT COUNT(user_usos_id)
    INTO ilosc_osob
    FROM users_groups
             JOIN unit_groups ug ON ug.unit_group_id = users_groups.group_id
             JOIN activities a ON ug.unit_group_id = a.unit_group
             JOIN rooms r ON a.room = r.room_id
    WHERE users_groups.group_id = grupa_id;


    IF ilosc_osob > rooms.capacity
    THEN
        wynik = FALSE;
    ELSE
        wynik = TRUE;

    END IF;
END
$$;
--2
CREATE OR REPLACE FUNCTION zajecia_w_danym_czasie(id_studenta IN users.usos_id%TYPE,
                                                  czas_rozpoczecia TIMESTAMP WITH TIME ZONE,
                                                  czas_zakonczenia TIMESTAMP WITH TIME ZONE)
    RETURNS bool
    LANGUAGE plpgsql
AS
$$
BEGIN
    CREATE TEMPORARY TABLE czas_temp
    (
        start_time TIMESTAMP WITH TIME ZONE NOT NULL,
        end_time   TIMESTAMP WITH TIME ZONE NOT NULL,
        unit_group INTEGER
    );

    SELECT start_time, end_time, unit_group
    INTO TABLE czas_temp
    FROM activities
        JOIN unit_groups ug
    ON activities.
    unit_group = ug.unit_group_id JOIN users_groups u ON ug.
    unit_group_id = u.group_id JOIN users u2 ON u2.
    usos_id = u.user_usos_id WHERE usos_id = id_studenta;
    FOR LOOP
    IF czas_temp.start_time = czas_rozpoczecia && czas_temp.end_time = czas_zakonczenia
    THEN
        RETURN FALSE
    ELSIF czas_temp.start_time != czas_rozpoczecia && czas_temp.end_time != czas_zakonczenia
    THEN
        RETURN TRUE
    END IF;
END loop; END $$;

-- 6
CREATE OR REPLACE FUNCTION ilosc_godzin_wykladowcy(wykladowca teachers.teacher_usos_id%TYPE) RETURNS FLOAT AS
$$
DECLARE
    zajecie     RECORD;
    grupa       INT;
    laczny_czas FLOAT:=0.0;
BEGIN
    FOR grupa IN SELECT unit_group FROM group_teacher WHERE teacher = wykladowca
        LOOP
            RAISE NOTICE 'Grupa %', grupa;
            FOR zajecie IN SELECT start_time, end_time FROM activities WHERE unit_group = grupa
                LOOP
                    laczny_czas := laczny_czas +
                                   EXTRACT(EPOCH FROM AGE(zajecie.end_time, zajecie.start_time)) / 3600 AS difference;
                END LOOP;
        END LOOP;
    RETURN laczny_czas;
END;
$$ LANGUAGE plpgsql;
SELECT ilosc_godzin_wykladowcy(186812);

-- 8
CREATE EXTENSION cube;
CREATE EXTENSION earthdistance;
CREATE OR REPLACE FUNCTION odleglosc_miedzy_budynkami(budynek_nr1 TEXT, budynek_nr2 TEXT)
    RETURNS FLOAT
    LANGUAGE plpgsql
AS
$$
DECLARE
    odleglosc FLOAT;
    punkt1    DOUBLE PRECISION;
    punkt2    DOUBLE PRECISION;

BEGIN
    SELECT POINT(longitude, latitude) <@> POINT(longitude, latitude) AS distance
    INTO odleglosc
    FROM buildings
    WHERE building_id = budynek_nr1
      AND building_id = budynek_nr2;
    RETURN odleglosc
END;
$$