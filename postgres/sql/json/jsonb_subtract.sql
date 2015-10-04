
CREATE OR REPLACE FUNCTION "jsonb_subtract"(
  "json" jsonb,
  "remove" TEXT
)
  RETURNS jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT
  CASE WHEN "json" ? "remove"
    THEN COALESCE(
      (SELECT json_object_agg("key", "value") FROM jsonb_each("json") WHERE "key" <> "remove"),
      '{}'
    )::jsonb
    ELSE "json"
END

$function$;


CREATE OR REPLACE FUNCTION "jsonb_subtract"(
  "json" jsonb,
  "keys" TEXT[]
)
  RETURNS jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$


SELECT CASE WHEN "json" ?| "keys" THEN COALESCE(
  (SELECT json_object_agg("key", "value") FROM jsonb_each("json") WHERE "key" <> ALL("keys")),
  '{}'::json
)::jsonb
ELSE "json"
END

$function$;

CREATE OR REPLACE FUNCTION "jsonb_subtract_obj"(
  "json" jsonb,
  "remove" jsonb
)
  RETURNS jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT COALESCE(json_object_agg("key", "value"), '{}'::json)::jsonb
FROM (
  SELECT key, value FROM jsonb_each("json")
  EXCEPT
  SELECT key, value FROM jsonb_each("remove")
) x

$function$;


CREATE OR REPLACE FUNCTION "jsonb_subtract"(
  "json" jsonb,
  "remove" json
)
  RETURNS jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT
  CASE
    WHEN json_typeof("remove") = 'array' THEN
      jsonb_subtract("json", json_array_elements_text("remove"))
    ELSE
      jsonb_subtract_obj("json", "remove"::jsonb)
  END

$function$;


CREATE OR REPLACE FUNCTION "jsonb_subtract"(
  "json" jsonb,
  "remove" jsonb
)
  RETURNS jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT
  CASE
    WHEN jsonb_typeof("remove") = 'array' THEN
      jsonb_subtract("json", jsonb_array_elements_text("remove"))
    ELSE
      jsonb_subtract_obj("json", "remove")
  END

$function$;


DROP OPERATOR IF EXISTS - (jsonb, text);
DROP OPERATOR IF EXISTS - (jsonb, text[]);
DROP OPERATOR IF EXISTS - (jsonb, json);
DROP OPERATOR IF EXISTS - (jsonb, jsonb);
CREATE OPERATOR - (LEFTARG = jsonb, RIGHTARG = text, PROCEDURE = jsonb_subtract);
CREATE OPERATOR - (LEFTARG = jsonb, RIGHTARG = text[], PROCEDURE = jsonb_subtract);
CREATE OPERATOR - (LEFTARG = jsonb, RIGHTARG = json, PROCEDURE = jsonb_subtract);
CREATE OPERATOR - (LEFTARG = jsonb, RIGHTARG = jsonb, PROCEDURE = jsonb_subtract);