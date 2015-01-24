CREATE OR REPLACE FUNCTION "jsonb_update_only_if_present"(
  "json" jsonb,
  "other" json
)
  RETURNS jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT COALESCE(json_object_agg("key", "value"), '{}'::json)::jsonb
FROM (
  SELECT "key", "value"
  FROM jsonb_each("json")

  UNION ALL

  SELECT "key", "value"::jsonb
  FROM json_each("other")
  WHERE "json" ? "key"::text
) x

$function$;

CREATE OR REPLACE FUNCTION "jsonb_update_only_if_present"(
  "json" jsonb,
  "other" jsonb
)
  RETURNS jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT COALESCE(json_object_agg("key", "value"), '{}'::json)::jsonb
FROM (
  SELECT "key", "value"
  FROM jsonb_each("json")

  UNION ALL

  SELECT "key", "value"
  FROM jsonb_each("other")
  WHERE "json" ? "key"::text
) x

$function$;

DROP OPERATOR IF EXISTS #= (jsonb, json);
DROP OPERATOR IF EXISTS #= (jsonb, jsonb);
CREATE OPERATOR #= (LEFTARG = jsonb, RIGHTARG = json, PROCEDURE = jsonb_update_only_if_present);
CREATE OPERATOR #= (LEFTARG = jsonb, RIGHTARG = jsonb, PROCEDURE = jsonb_update_only_if_present);


