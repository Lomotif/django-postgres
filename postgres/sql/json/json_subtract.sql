BEGIN;

CREATE OR REPLACE FUNCTION "json_subtract"(
  "json" json,
  "remove" TEXT
)
  RETURNS json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT
  CASE WHEN "json"::jsonb ? "remove"
    THEN COALESCE(
      (SELECT json_object_agg("key", "value") FROM json_each("json") WHERE "key" <> "remove"),
      '{}'::json
    )
    ELSE "json"
END

$function$;


CREATE OR REPLACE FUNCTION "json_subtract"(
  "json" json,
  "keys" TEXT[]
)
  RETURNS json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT CASE WHEN "json"::jsonb ?| "keys" THEN COALESCE(
  (SELECT json_object_agg("key", "value") FROM json_each("json") WHERE "key" <> ALL("keys")),
  '{}'::json
)
ELSE "json"
END

$function$;

CREATE OR REPLACE FUNCTION "json_subtract_obj"(
  "json" json,
  "remove" jsonb
)
  RETURNS json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT COALESCE(json_object_agg("key", "value"), '{}'::json)
FROM (
  SELECT key, value::jsonb FROM json_each("json")
  EXCEPT
  SELECT key, value FROM jsonb_each("remove")
) x

$function$;

CREATE OR REPLACE FUNCTION "json_subtract"(
  "json" json,
  "remove" json
)
  RETURNS json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT
  CASE
    WHEN json_typeof("remove") = 'array' THEN
      json_subtract("json", json_array_elements_text("remove"))
    ELSE
      json_subtract_obj("json", "remove"::jsonb)
  END

$function$;


CREATE OR REPLACE FUNCTION "json_subtract"(
  "json" json,
  "remove" jsonb
)
  RETURNS json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT
  CASE
    WHEN jsonb_typeof("remove") = 'array' THEN
      json_subtract("json", jsonb_array_elements_text("remove"))
    ELSE
      json_subtract_obj("json", "remove")
  END

$function$;


DROP OPERATOR IF EXISTS - (json, text);
DROP OPERATOR IF EXISTS - (json, text[]);
DROP OPERATOR IF EXISTS - (json, json);
DROP OPERATOR IF EXISTS - (json, jsonb);
CREATE OPERATOR - (LEFTARG = json, RIGHTARG = text, PROCEDURE = json_subtract);
CREATE OPERATOR - (LEFTARG = json, RIGHTARG = text[], PROCEDURE = json_subtract);
CREATE OPERATOR - (LEFTARG = json, RIGHTARG = json, PROCEDURE = json_subtract);
CREATE OPERATOR - (LEFTARG = json, RIGHTARG = jsonb, PROCEDURE = json_subtract);


COMMIT;