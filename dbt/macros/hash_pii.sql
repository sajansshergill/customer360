{% macro hash_pii(column_expr, salt=var('pii_salt', 'dev-salt')) %}
    sha256(concat('{{ salt }}:', lower(trim(cast({{ column_expr }} as varchar)))))
{% endmacro %}
