--
-- Functions an operators that bring some of the hstore goodnes
-- to the JSONB datatype.
--

CREATE OR REPLACE FUNCTION "json_concatenate"(
  "json" json,
  "other" json
)
  RETURNS json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM (SELECT * FROM json_each("json") UNION ALL SELECT * FROM json_each("other")) AS a
  ),
  '{}'
)::json
$function$;


CREATE OR REPLACE FUNCTION "json_concatenate"(
  "json" json,
  "other" jsonb
)
  RETURNS json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM (SELECT * FROM json_each("json") UNION ALL SELECT * FROM json_each("other"::json)) AS a
  ),
  '{}'
)::json
$function$;

DROP OPERATOR IF EXISTS || (json, json);
DROP OPERATOR IF EXISTS || (json, jsonb);
CREATE OPERATOR || (LEFTARG = json, RIGHTARG = json, PROCEDURE = json_concatenate);
CREATE OPERATOR || (LEFTARG = json, RIGHTARG = jsonb, PROCEDURE = json_concatenate);


CREATE OR REPLACE FUNCTION "jsonb_concatenate"(
  "json" jsonb,
  "other" json
)
  RETURNS jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM (SELECT * FROM jsonb_each("json") UNION ALL SELECT * FROM jsonb_each("other"::jsonb)) AS a
  ),
  '{}'
)::jsonb
$function$;


CREATE OR REPLACE FUNCTION "jsonb_concatenate"(
  "json" jsonb,
  "other" jsonb
)
  RETURNS jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM (SELECT * FROM jsonb_each("json") UNION ALL SELECT * FROM jsonb_each("other")) AS a
  ),
  '{}'
)::jsonb
$function$;

DROP OPERATOR IF EXISTS || (jsonb, json);
DROP OPERATOR IF EXISTS || (jsonb, jsonb);
CREATE OPERATOR || (LEFTARG = jsonb, RIGHTARG = json, PROCEDURE = jsonb_concatenate);
CREATE OPERATOR || (LEFTARG = jsonb, RIGHTARG = jsonb, PROCEDURE = jsonb_concatenate);



CREATE OR REPLACE FUNCTION "json_update_only_if_present"(
  "json" json,
  "other" json
)
  RETURNS json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM (SELECT * FROM json_each("json") UNION ALL SELECT * FROM json_each("other")) AS a
     WHERE "json"::jsonb ? "key"::text
  ),
  '{}'
)::jsonb::json
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

SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM (SELECT * FROM json_each("json") UNION ALL SELECT * FROM json_each("other"::json)) AS a
     WHERE "json"::jsonb ? "key"::text
  ),
  '{}'
)::jsonb::json
$function$;

DROP OPERATOR IF EXISTS #= (json, json);
DROP OPERATOR IF EXISTS #= (json, jsonb);
CREATE OPERATOR #= (LEFTARG = json, RIGHTARG = json, PROCEDURE = json_update_only_if_present);
CREATE OPERATOR #= (LEFTARG = json, RIGHTARG = jsonb, PROCEDURE = json_update_only_if_present);


CREATE OR REPLACE FUNCTION "jsonb_update_only_if_present"(
  "json" jsonb,
  "other" json
)
  RETURNS jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$

SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM (SELECT * FROM jsonb_each("json") UNION ALL SELECT * FROM jsonb_each("other"::jsonb)) AS a
     WHERE "json" ? "key"::text
  ),
  '{}'
)::jsonb
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

SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM (SELECT * FROM jsonb_each("json") UNION ALL SELECT * FROM jsonb_each("other")) AS a
     WHERE "json" ? "key"::text
  ),
  '{}'
)::jsonb
$function$;

DROP OPERATOR IF EXISTS #= (jsonb, json);
DROP OPERATOR IF EXISTS #= (jsonb, jsonb);
CREATE OPERATOR #= (LEFTARG = jsonb, RIGHTARG = json, PROCEDURE = jsonb_update_only_if_present);
CREATE OPERATOR #= (LEFTARG = jsonb, RIGHTARG = jsonb, PROCEDURE = jsonb_update_only_if_present);


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



-- Operator: -
-- ARG[0], RETURN json

CREATE OR REPLACE FUNCTION "json_subtract"(
  "json" json,
  "remove" TEXT
)
  RETURNS json
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$
SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM json_each("json")
    WHERE "key" <> "remove"),
  '{}'
)::json
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
SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM json_each("json")
    WHERE "key" <> ALL ("keys")),
  '{}'
)::json
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
SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM json_each("json")
    WHERE "json"->>"key" <> ("remove"->>"key")),
  '{}'
)::json
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
SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM json_each("json")
    WHERE "json"->>"key" <> ("remove"->>"key")),
  '{}'
)::json
$function$;


DROP OPERATOR IF EXISTS - (json, text);
DROP OPERATOR IF EXISTS - (json, text[]);
DROP OPERATOR IF EXISTS - (json, json);
DROP OPERATOR IF EXISTS - (json, jsonb);
CREATE OPERATOR - (LEFTARG = json, RIGHTARG = text, PROCEDURE = json_subtract);
CREATE OPERATOR - (LEFTARG = json, RIGHTARG = text[], PROCEDURE = json_subtract);
CREATE OPERATOR - (LEFTARG = json, RIGHTARG = json, PROCEDURE = json_subtract);
CREATE OPERATOR - (LEFTARG = json, RIGHTARG = jsonb, PROCEDURE = json_subtract);

-- Operator: -
-- ARG[0], RETURN jsonb

CREATE OR REPLACE FUNCTION "jsonb_subtract"(
  "json" jsonb,
  "remove" TEXT
)
  RETURNS jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $function$
SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM jsonb_each("json") -- Until this function is added!
    WHERE "key" <> "remove"),
  '{}'
)::jsonb
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
SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM jsonb_each("json")
    WHERE "key" <> ALL ("keys")),
  '{}'
)::jsonb
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
SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM jsonb_each("json")
    WHERE "json"->>"key" <> ("remove"->>"key")),
  '{}'
)::jsonb
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
SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM jsonb_each("json")
    WHERE "json"->>"key" <> ("remove"->>"key")),
  '{}'
)::jsonb
$function$;


DROP OPERATOR IF EXISTS - (jsonb, text);
DROP OPERATOR IF EXISTS - (jsonb, text[]);
DROP OPERATOR IF EXISTS - (jsonb, json);
DROP OPERATOR IF EXISTS - (jsonb, jsonb);
CREATE OPERATOR - (LEFTARG = jsonb, RIGHTARG = text, PROCEDURE = jsonb_subtract);
CREATE OPERATOR - (LEFTARG = jsonb, RIGHTARG = text[], PROCEDURE = jsonb_subtract);
CREATE OPERATOR - (LEFTARG = jsonb, RIGHTARG = json, PROCEDURE = jsonb_subtract);
CREATE OPERATOR - (LEFTARG = jsonb, RIGHTARG = jsonb, PROCEDURE = jsonb_subtract);
