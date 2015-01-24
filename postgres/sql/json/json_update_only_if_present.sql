CREATE OR REPLACE FUNCTION "json_update_only_if_present"(
  "json" json,
  "other" json
)
  RETURNS json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT COALESCE(json_object_agg("key", "value"), '{}'::json)
FROM (
  SELECT "key", "value"
  FROM json_each("json")

  UNION ALL

  SELECT "key", "value"
  FROM json_each("other")
  WHERE "json"::jsonb ? "key"::text
) x

$function$;

CREATE OR REPLACE FUNCTION "json_update_only_if_present"(
  "json" json,
  "other" jsonb
)
  RETURNS json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT COALESCE(json_object_agg("key", "value"), '{}'::json)
FROM (
  SELECT "key", "value"
  FROM json_each("json")

  UNION ALL

  SELECT "key", "value"::json
  FROM jsonb_each("other")
  WHERE "json"::jsonb ? "key"::text
) x

$function$;

DROP OPERATOR IF EXISTS #= (json, json);
DROP OPERATOR IF EXISTS #= (json, jsonb);
CREATE OPERATOR #= (LEFTARG = json, RIGHTARG = json, PROCEDURE = json_update_only_if_present);
CREATE OPERATOR #= (LEFTARG = json, RIGHTARG = jsonb, PROCEDURE = json_update_only_if_present);
