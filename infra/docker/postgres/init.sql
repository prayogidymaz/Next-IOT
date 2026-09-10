-- Next-IOT: PostgreSQL init script (runs once on first container start)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Isolated DB for pytest (keeps dev seed data intact)
CREATE DATABASE next_iot_test;
