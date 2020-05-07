-- создаем таблицу dash_engagement
CREATE TABLE dash_engagement(record_id serial PRIMARY KEY,
                             dt TIMESTAMP,
                             item_topic VARCHAR(256),
                             event VARCHAR(256),
                             age_segment VARCHAR(256),
                             unique_users BIGINT
                            );
-- назначаем полный доступ к таблице
-- вместо **** должно быть имя пользователя
GRANT ALL PRIVILEGES ON TABLE dash_engagement TO ****;
-- назначаем полный доступ к первичному ключу
GRANT USAGE, SELECT ON SEQUENCE dash_engagement_record_id_seq TO ****;
