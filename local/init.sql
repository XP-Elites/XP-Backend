CREATE TYPE statustypes as ENUM (
'IN_QUEUE', 'PROCESSING', 'COMPLETE', 'ERROR'
);

CREATE TABLE job_status (
    uuid UUID,
    status statustypes
);