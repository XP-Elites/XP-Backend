CREATE TYPE status_types AS ENUM (
    'IN_QUEUE',
    'PROCESSING',
    'COMPLETE',
    'ERROR'
);

CREATE TABLE job_status (
    uuid UUID PRIMARY KEY,
    status status_types NOT NULL DEFAULT 'IN_QUEUE'
);