-- ATTENTION!
-- EXECUTING THIS SQL SCRIPT MAY CAUSE ALL DATA LOSS!
-- USE ONLY FOR TEST AND DEBUGGING PURPOSES!
SELECT 'drop table if exists "' || tables.table_name || '" cascade;'
FROM   information_schema.tables
WHERE  table_schema = 'public';
