{{ config(materialized="table") }}

select sum(basefare)
from iceberg_scan("s3://wizbiicebergtesting/testdb/iceberg_29gb/metadata/00000-bcde336c-c514-4349-9212-0b464037bf8e.metadata.json")
group by flightdate;