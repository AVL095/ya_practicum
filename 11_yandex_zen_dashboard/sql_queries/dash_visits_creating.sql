-- создаем таблицу dash_visits
CREATE TABLE dash_visits(record_id serial PRIMARY KEY,       
                         item_topic VARCHAR(256),
                         source_topic VARCHAR(256),
                         age_segment VARCHAR(256),
                         dt TIMESTAMP,
                         visits INT);                  
-- назначаем полный доступ к таблице
-- вместо **** должно быть имя пользователя
GRANT ALL PRIVILEGES ON TABLE dash_visits TO ****;
-- назначаем полный доступ к первичному ключу
GRANT USAGE, SELECT ON SEQUENCE dash_visits_record_id_seq TO ****;