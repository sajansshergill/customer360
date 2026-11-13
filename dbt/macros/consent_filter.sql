{% macro consent_filter(profile_alias='p') %}
    {{ profile_alias }}.marketing_consent = true
{% endmacro %}
