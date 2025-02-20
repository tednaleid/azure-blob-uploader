CREATE TABLE test_files (
    id SERIAL PRIMARY KEY,
    xml_content TEXT NOT NULL
);

-- Insert some test XML files
INSERT INTO test_files (xml_content) 
SELECT 
    format(
        '<root><id>%s</id><data>Test data for record %s</data><timestamp>%s</timestamp></root>',
        generate_series,
        generate_series,
        now() - (generate_series || ' hours')::interval
    )
FROM generate_series(1, 1000);