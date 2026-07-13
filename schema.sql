-- schema.sql
-- Creates the dba_tickets database and tickets table
-- Run this in pgAdmin Query Tool

-- Step 1: Run this line first in pgAdmin
-- connected to the default 'postgres' database
CREATE DATABASE dba_tickets;

-- Step 2: Switch to dba_tickets database in pgAdmin
-- then run everything below

-- Step 3: Create the tickets table
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id       SERIAL          PRIMARY KEY,
    client_name     VARCHAR(100)    NOT NULL,
    issue_title     VARCHAR(200)    NOT NULL,
    description     TEXT,
    priority        VARCHAR(20)     DEFAULT 'Medium'
                    CHECK (priority IN
                        ('Critical','High','Medium','Low')),
    status          VARCHAR(20)     DEFAULT 'Open'
                    CHECK (status IN
                        ('Open','In Progress','Resolved')),
    assigned_to     VARCHAR(100)    DEFAULT 'Jean Pierre Idi',
    created_at      TIMESTAMP       DEFAULT NOW(),
    resolved_at     TIMESTAMP,
    time_spent_mins INTEGER         DEFAULT 0,
    resolution      TEXT
);

-- Step 4: Verify the table was created
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'tickets'
ORDER BY ordinal_position;