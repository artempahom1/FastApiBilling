SELECT 'CREATE DATABASE billing'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'billing')\gexec