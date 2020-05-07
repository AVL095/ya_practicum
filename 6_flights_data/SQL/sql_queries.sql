-- 1 запрос
/* 
Изучите таблицу airports и выведите
список городов (city), в которых есть аэропорты.
*/
SELECT 
    DISTINCT city 
FROM airports

-- 2 запрос
/* 
Изучите таблицу flights и подсчитайте количество вылетов (flight_id)
из каждого аэропорта вылета (departure_airport).
Назовите переменную cnt_flights и выведите её вместе со столбцом departure_airport.
Результат отсортируйте в порядке убывания количества вылетов.
*/
SELECT 
    departure_airport,
    COUNT(flight_id) AS cnt_flights 
FROM flights
GROUP BY departure_airport
ORDER BY cnt_flights DESC;

-- 3 запрос
/* 
Найдите количество рейсов на каждой модели самолёта с вылетом в сентябре 2018 года.
Назовите получившееся поле flights_amount и выведите его, также выведите поле model.
Столбцы в таблице должны быть выведены в следующем порядке: - model - flights_amount
*/
SELECT
    aircrafts.model AS model,
    COUNT(flights.flight_id) AS flights_amount 
FROM
flights
RIGHT JOIN aircrafts ON aircrafts.aircraft_code=flights.aircraft_code
WHERE EXTRACT(MONTH FROM departure_time)='9'
GROUP BY 
aircrafts.model;

-- 4 запрос
/* 
Посчитайте количество рейсов по всем моделям самолетов Boeing и Airbus в сентябре.
Назовите получившуюся переменную flights_amount и выведите ее.
*/
SELECT 
    COUNT(flights.flight_id) AS flights_amount
FROM
    aircrafts
RIGHT JOIN flights ON flights.aircraft_code=aircrafts.aircraft_code
WHERE EXTRACT(MONTH FROM departure_time)='9'AND model IN
    (
     SELECT
     aircrafts.model AS model
     FROM 
     aircrafts     
     WHERE aircrafts.model LIKE '%Boeing%'
    )
UNION ALL
SELECT 
    COUNT(flights.flight_id) AS flights_amount
FROM
    aircrafts
RIGHT JOIN flights ON flights.aircraft_code=aircrafts.aircraft_code
WHERE EXTRACT(MONTH FROM departure_time)='9'AND model IN
    (
     SELECT
     aircrafts.model AS model
     FROM 
     aircrafts     
     WHERE aircrafts.model LIKE '%Airbus%'
    )

-- 5 запрос
/* 
Посчитайте среднее количество прибывающих рейсов в день для каждого города за август 2018 года.
Назовите получившееся поле average_flights , вместе с ней выведите столбец city.
Столбцы в таблице должны быть выведены в следующем порядке: - city - average_flights
*/
SELECT 
    flights_august.city AS city,
    (AVG(flights_august.flight_id_count)) AS average_flights
FROM    
    (SELECT 
        airports.city AS city,
        COUNT(flights.flight_id) AS flight_id_count,
        EXTRACT(DAY FROM flights.arrival_time::date)
    FROM 
       flights
    INNER JOIN airports ON flights.arrival_airport = airports.airport_code
    WHERE 
         EXTRACT(MONTH FROM flights.arrival_time::date)='8' AND
         EXTRACT(YEAR FROM flights.arrival_time::date)='2018'
    GROUP BY 
        airports.city,
        EXTRACT(DAY FROM flights.arrival_time::date)) AS flights_august
GROUP BY
    flights_august.city

-- 6 запрос
/* 
Установите фестивали, которые проходили с 23 июля по 30 сентября 2018 года в Москве,
и номер недели, в которую они проходили.
Выведите название фестиваля festival_name и номер недели festival_week.
*/
SELECT
festival_name,
EXTRACT (WEEK FROM festival_date::date) AS festival_week
FROM
festivals
WHERE 
    festival_date::date>='2018-07-23' AND
    festival_date::date<='2018-09-30' AND
    festival_city='Москва'

-- 7 запрос
/* 
Для каждой недели с 23 июля по 30 сентября 2018 года посчитайте количество билетов,
купленных на рейсы в Москву (номер недели week_number и количество билетов ticket_amount).
Получите таблицу, в которой будет информация о количестве купленных за неделю билетов; отметка,
проходил ли в эту неделю фестиваль; название фестиваля festival_name и номер недели week_number.
Столбцы в таблице должны быть выведены в следующем порядке:
- week_number - ticket_amount - festival_week - festival_name
*/
SELECT
EXTRACT (WEEK FROM flights.arrival_time) AS week_number,
COUNT(ticket_flights.ticket_no) AS ticket_amount,
subq.festival_week AS festival_week,
subq.festival_name AS festival_name
FROM
flights
LEFT JOIN ticket_flights ON flights.flight_id=ticket_flights.flight_id
LEFT JOIN airports ON flights.arrival_airport=airports.airport_code
LEFT JOIN 
        (SELECT
        festival_name,
        festival_city,
        festival_date,
        EXTRACT (WEEK FROM festival_date::date) AS festival_week
        FROM
        festivals
        WHERE 
        festivals.festival_date::date>='2018-07-23' AND
        festivals.festival_date::date<='2018-09-30' AND
        festivals.festival_city='Москва') AS subq ON EXTRACT(WEEK FROM flights.arrival_time)=EXTRACT(WEEK FROM festival_date::date)
WHERE
airports.city='Москва' AND 
(flights.arrival_time::date) BETWEEN '2018-07-23' AND '2018-09-30'
GROUP BY
week_number,
festival_week,
festival_name
ORDER BY
week_number;
