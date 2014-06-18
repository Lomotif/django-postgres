-- In order to reimplement the JSONB functions, we need to
-- essentially create a canonical "version" of the json object,
-- so we can compare, etc.

CREATE OR REPLACE FUNCTION "canonical" ("json" json)
RETURNS json
LANGUAGE sql
IMMUTABLE
STRICT
AS $function$

SELECT
  CASE
    WHEN ascii("json"::text) = 123 THEN
      -- Object (ascii == 123).
      COALESCE(
        (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
        FROM (SELECT DISTINCT ON("key") "key", "value" FROM json_each("json") ORDER BY "key") as x
        ), '{}'
      )::json
    ELSE "json"
      -- All other types, just leave as-is.
  END;
$function$;


CREATE OR REPLACE FUNCTION "json_equality" (
  "left" json, "right" json
) RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE STRICT
AS $function$

  SELECT canonical("left")::text = canonical("right")::text;

$function$;

CREATE OR REPLACE FUNCTION "json_inequality" (
  "left" json, "right" json
) RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE STRICT AS $function$

  SELECT canonical("left")::text <> canonical("right")::text;

$function$;

CREATE OPERATOR = (
  LEFTARG = json,
  RIGHTARG = json,
  PROCEDURE = json_equality,
  COMMUTATOR = =,
  NEGATOR = <>
);

CREATE OPERATOR <> (
  LEFTARG = json,
  RIGHTARG = json,
  PROCEDURE = json_inequality,
  COMMUTATOR = <>,
  NEGATOR = =
);


CREATE OR REPLACE FUNCTION "json_contains" (
  "left" json, "right" json
) RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE STRICT AS $function$

SELECT
  CASE
    WHEN ascii("left"::text) = 123 AND ascii("right"::text) = 123 THEN
      (SELECT count(*)=0 FROM
        json_each("left") l
        FULL OUTER JOIN
        json_each("right") r
        ON (l.key = r.key AND l.value = r.value)
        WHERE l.key IS NULL)
    WHEN ascii("left"::text) = 91 AND ascii("right"::text) = 91 THEN
      (SELECT count(*)=0 FROM
        json_array_elements("right")  WHERE value NOT IN (
        SELECT * FROM json_array_elements("left")
      ))
    ELSE false
  END;

$function$;

CREATE OPERATOR @> (
  LEFTARG = json, RIGHTARG = json,
  PROCEDURE = json_contains,
  COMMUTATOR = <@
);


CREATE OR REPLACE FUNCTION "json_contained" (
  "left" json, "right" json
) RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE STRICT AS $function$

  SELECT json_contains("right", "left");

$function$;

CREATE OPERATOR <@ (
  LEFTARG = json, RIGHTARG = json,
  PROCEDURE = json_contained,
  COMMUTATOR = @>
);


CREATE OR REPLACE FUNCTION "json_has_key" (
  "left" json, "target" text
) RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE STRICT AS $function$

SELECT
  CASE
    WHEN ascii("left"::text) = 91 THEN
      -- array
      (SELECT count(*) > 0 FROM json_array_elements("left") WHERE value::text = "target")
    WHEN ascii("left"::text) = 123 THEN
      -- object
      (SELECT count(*) > 0 FROM json_each("left") WHERE "key" = "target")
    ELSE false
  END;

$function$;

CREATE OPERATOR ? (
  LEFTARG = json,
  RIGHTARG = text,
  PROCEDURE = json_has_key
);

CREATE OR REPLACE FUNCTION "json_has_all_keys" (
  "left" json, "target" text[]
) RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE STRICT AS $function$

SELECT
  CASE
    WHEN ascii("left"::text) = 91 THEN
      -- array
      (SELECT count(*) = 0 FROM json_array_elements("left") l FULL OUTER JOIN unnest("target") t ON (l.value::text = t) WHERE l.value IS NULL)
    WHEN ascii("left"::text) = 123 THEN
      -- object
      (SELECT count(*) = 0 FROM json_each("left") l FULL OUTER JOIN unnest("target") t ON (l.key::text = t) WHERE l.key IS NULL)
    ELSE false
  END;

$function$;

CREATE OPERATOR ?& (
  LEFTARG = json,
  RIGHTARG = text[],
  PROCEDURE = json_has_all_keys
);


CREATE OR REPLACE FUNCTION "json_has_any_keys" (
  "left" json, "target" text[]
) RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE STRICT AS $function$

SELECT
  CASE
    WHEN ascii("left"::text) = 91 THEN
      -- array
      (SELECT count(*) > 0 FROM json_array_elements("left") l RIGHT OUTER JOIN unnest("target") t ON (l.value::text = t) WHERE l.value IS NOT NULL)
    WHEN ascii("left"::text) = 123 THEN
      -- object
      (SELECT count(*) > 0 FROM json_each("left") l RIGHT OUTER JOIN unnest("target") t ON (l.key::text = t) WHERE l.key IS NOT NULL)
    ELSE false
  END;

$function$;

CREATE OPERATOR ?| (
  LEFTARG = json,
  RIGHTARG = text[],
  PROCEDURE = json_has_any_keys
);