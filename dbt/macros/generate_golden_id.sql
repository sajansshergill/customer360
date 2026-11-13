{% macro generate_golden_id(email_column) %}
    {{ hash_pii(email_column) }}
{% endmacro %}
