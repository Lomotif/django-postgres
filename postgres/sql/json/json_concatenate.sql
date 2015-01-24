BEGIN;

CREATE OR REPLACE FUNCTION "json_concatenate" (
  "json" json, "other" json
)
  RETURNS json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $$

  SELECT COALESCE(json_object_agg(key, value), '{}'::json) FROM (
    SELECT key, value::jsonb FROM json_each("json")
    UNION ALL
    SELECT key, value::jsonb FROM json_each("other")
  ) x;

$$;

CREATE OR REPLACE FUNCTION "json_concatenate" (
  "json" json, "other" jsonb
)
  RETURNS json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $$

  SELECT COALESCE(json_object_agg(key, value), '{}'::json) FROM (
    SELECT key, value::jsonb FROM json_each("json")
    UNION ALL
    SELECT key, value FROM jsonb_each("other")
  ) x;

$$;

DROP OPERATOR IF EXISTS || (json, json);
DROP OPERATOR IF EXISTS || (json, jsonb);
CREATE OPERATOR || (LEFTARG = json, RIGHTARG = json, PROCEDURE = json_concatenate);
CREATE OPERATOR || (LEFTARG = json, RIGHTARG = jsonb, PROCEDURE = json_concatenate);

COMMIT;