-- This file should contain all code required to create & seed database tables.

DROP DATABASE IF EXISTS museum;
CREATE DATABASE museum;

\c museum;

CREATE TABLE IF NOT EXISTS exhibition (
    exhibition_id INT GENERATED ALWAYS AS IDENTITY (MINVALUE 0 START WITH 0 INCREMENT BY 1) PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    floor TEXT NOT NULL,
    department TEXT,
    start_date DATE DEFAULT CURRENT_DATE,
    description TEXT UNIQUE,
    CONSTRAINT description_not_empty_chk CHECK (LENGTH(description) > 0),
    CONSTRAINT exhibition_floor_chk CHECK (floor IN ('1', '2', '3', '4', 'Vault')),
    CONSTRAINT name_not_empty_chk CHECK (LENGTH(name) > 0),
    CONSTRAINT department_not_empty_chk CHECK (LENGTH(department) > 0),
    CONSTRAINT unique_entry_exhibition UNIQUE (name, floor, department, start_date, description)
);


CREATE TABLE IF NOT EXISTS kiosk_transaction (
    kiosk_transaction_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    transaction_date DATE NOT NULL,
    transaction_time TIME NOT NULL,
    exhibition_id INT NOT NULL,
    value INT,
    type TEXT,
    CONSTRAINT kiosk_transaction_type_chk CHECK (type IN ('emergency','assistance')),
    CONSTRAINT kiosk_value_chk CHECK (value BETWEEN 0 AND 4),
    CONSTRAINT transaction_date_not_future CHECK (transaction_date <= CURRENT_DATE),
    CONSTRAINT fk_exhibition FOREIGN KEY (exhibition_id) REFERENCES exhibition(exhibition_id),
    CONSTRAINT unique_entry_kiosk UNIQUE (transaction_date, transaction_time, exhibition_id, type, value) 
);
