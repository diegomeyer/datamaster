-- Criação dos databases
CREATE DATABASE metastore;
--CREATE DATABASE IF NOT EXISTS airflow;

-- Criação dos usuários
CREATE USER hive WITH ENCRYPTED PASSWORD 'hive';
--CREATE USER airflow WITH ENCRYPTED PASSWORD 'airflow';

-- Concede ownership total dos bancos
ALTER DATABASE metastore OWNER TO hive;
ALTER DATABASE airflow OWNER TO airflow;

-- Concede permissões totais nos bancos
GRANT ALL PRIVILEGES ON DATABASE metastore TO hive;
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;

ALTER ROLE hive WITH SUPERUSER;
ALTER ROLE hive WITH CREATEROLE;
ALTER ROLE hive WITH CREATEDB;
ALTER ROLE hive WITH REPLICATION;
ALTER ROLE hive WITH BYPASSRLS;

---- Opcional: garante que futuros objetos tenham permissões
--\connect metastore
--GRANT ALL ON SCHEMA public TO metastore;
--ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO hive;
--ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO hive;
--
--\connect airflow
--GRANT ALL ON SCHEMA public TO airflow;
--ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO airflow;
--ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO airflow;
