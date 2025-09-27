{{ "{{" }} config(materialized="table") {{ "}}" }}

select {{ group_by_columns }} , {{ aggr_func }}({{ column_name }})
from {{ table_name }}
group by {{ group_by_columns }}