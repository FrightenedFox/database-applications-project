### Funkcje

1. **Sprawdzić, czy w grupie są wolne miejsca.**

   W tym celu potrzebujemy stworzyć funkcję, która przyjmuje jako parametr `unit_groups.unit_group_id` i zwraca
   wartość `True`, jeżeli jest przynajmniej jedno wolne miejsce, i `False` w przeciwnym wypadku. Ilość wolnych miejsc
   otrzymujemy, przeglądając wszystkie zajęcia grupy i poszukując salę z najmniejszą pojemnością (`rooms.capacity`).

2. **Sprawdź, czy student nie ma zajęć w pewnym odcinku czasowym.**

   Funkcja powinna przyjmować id użytkownika (`users.usos_id`), czas początkowy (w formacie datetime, czyli data z
   czasem) i czas końcowy. Wynikiem działania funkcji powinna być wartość `True`, jeżeli student nie ma zajęć w
   określonym czasie, i `False` w przeciwnym wypadku.

3. **Sprawdź, czy prowadzący nie ma zajęć w pewnym odcinku czasowym.**

   Analogicznie jak punkt 2, tylko dla prowadzącego (`teachers.teacher_usos_id`).

4. **Sprawdź, czy grupa nie ma zajęć w pewny odcinku czasowym.**

   Analogicznie jak punkt 2, tylko dla grupy (`unit_groups.unit_group_id`).

5. **Sprawdź, czy sala jest wolna w pewnym odcinku czasowym.**

   Analogicznie jak punkt 2, tylko dla sali (`rooms.room_id`).

6. **Łączna liczba godzin pracy prowadzącego.**

   Funkcja przyjmuje id prowadzącego (`teachers.teacher_usos_id`) i zwraca sumarną liczbę godzin pracy prowadzącego.

7. **Łączna liczba godzin pracy studenta.**

   Analogicznie jak punkt 6, tylko dla studenta (`users.usos_id`).

8. **Policz odległość pomiędzy dwoma punktami A i B za ich współrzędnymi geograficznymi.**

   Funkcja przyjmuje dwie wartości: id budynku A i budynku B (`buildings.building_id`). Wynikiem działania funkcji
   powinna być odległość w metrach pomiędzy budynkami. Do tego wykorzystujemy długość i szerokość geograficzną w
   tabeli `buildings`.