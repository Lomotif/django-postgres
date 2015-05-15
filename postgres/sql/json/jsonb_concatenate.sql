BEGIN;

CREATE OR REPLACE FUNCTION "jsonb_concatenate" (
  "json" jsonb, "other" json
)
  RETURNS jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $$

  SELECT COALESCE(json_object_agg(key, value), '{}'::json)::jsonb FROM (
    SELECT key, value FROM jsonb_each("json")
    UNION ALL
    SELECT key, value::jsonb FROM json_each("other")
  ) x;

$$;

CREATE OR REPLACE FUNCTION "jsonb_concatenate" (
  "json" jsonb, "other" jsonb
)
  RETURNS jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $$

  SELECT COALESCE(json_object_agg(key, value), '{}'::json)::jsonb FROM (
    SELECT key, value FROM jsonb_each("json")
    UNION ALL
    SELECT key, value FROM jsonb_each("other")
  ) x;

$$;

DROP OPERATOR IF EXISTS || (jsonb, json);
DROP OPERATOR IF EXISTS || (jsonb, jsonb);
CREATE OPERATOR || (LEFTARG = jsonb, RIGHTARG = json, PROCEDURE = jsonb_concatenate);
CREATE OPERATOR || (LEFTARG = jsonb, RIGHTARG = jsonb, PROCEDURE = jsonb_concatenate);

COMMIT;