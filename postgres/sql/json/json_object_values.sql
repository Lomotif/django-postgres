
CREATE OR REPLACE FUNCTION "json_object_values"(
  "json" json
)
  RETURNS SETOF json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT value FROM json_each("json");

$function$;

CREATE OR REPLACE FUNCTION "jsonb_object_values"(
  "json" jsonb
)
  RETURNS SETOF jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT value FROM jsonb_each("json");

$function$;
