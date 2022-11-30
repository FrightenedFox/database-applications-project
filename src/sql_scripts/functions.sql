
-- 1
create or replace function sprawdzanie_wolnego_miejsca(grupa_id in unit_groups.unit_group_id%TYPE)
returns wynik
language plpgsql
as $$
declare
ilosc_osob integer
wynik bool
BEGIN
    SELECT count(user_usos_id) into ilosc_osob from users_groups
        JOIN unit_groups ug on ug.unit_group_id = users_groups.group_id
        JOIN activities a on ug.unit_group_id = a.unit_group
        JOIN rooms r on a.room = r.room_id where users_groups.group_id= grupa_id;


if ilosc_osob > rooms.capacity
    then wynik = FALSE;
    else
    wynik = TRUE;

end if;
end $$;
--2
create or replace function zajecia_w_danym_czasie(id_studenta in users.usos_id%TYPE,czas_rozpoczecia timestamp with time zone,
czas_zakonczenia timestamp with time zone)
returns bool
    language plpgsql
as $$
BEGIN
    CREATE TEMPORARY TABLE czas_temp(
        start_time timestamp with time zone NOT NULL,
        end_time timestamp with time zone NOT NULL,
        unit_group integer);

    SELECT start_time, end_time, unit_group INTO table czas_temp from activities
    JOIN unit_groups ug on activities.unit_group = ug.unit_group_id
    JOIN users_groups u on ug.unit_group_id = u.group_id
    JOIN users u2 on u2.usos_id = u.user_usos_id where usos_id = id_studenta;
for loop
        if czas_temp.start_time = czas_rozpoczecia && czas_temp.end_time = czas_zakonczenia
            then return FALSE
        elsif czas_temp.start_time != czas_rozpoczecia && czas_temp.end_time != czas_zakonczenia
            then return TRUE
        end if;
    end loop;
    end $$;

-- 6
create or replace procedure ilosc_godzin_wykladowcy(wykladowca in teachers.teacher_usos_id%TYPE)
language plpgsql
as $$
DECLARE

zajecia record;
grupy int[];
czas1 integer;
czas2 integer;
Begin
    for grupy IN SELECT unit_group from group_teacher where teacher= wykladowca
    loop
    end loop;
FOR zajecia IN SELECT start_time, end_time from activities where unit_group = grupy
        loop
        czas1 := age(activities.end_time, activities.start_time) AS difference;
        czas2 := czas2+czas1;
        end loop;
end;
$$


-- 8
create extension cube;
create extension earthdistance;
create or replace function odleglosc_miedzy_budynkami(budynek_nr1 text, budynek_nr2 text)
returns float
    language plpgsql
as $$
declare
odleglosc float;
punkt1 double precision;
punkt2 double precision;

begin
    select point(longitude,latitude) <@> point(longitude,latitude) as distance into odleglosc
    from buildings where building_id=budynek_nr1 and building_id=budynek_nr2;
return odleglosc
end; $$