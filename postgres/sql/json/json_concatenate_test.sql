BEGIN;

-- Note: we need to cast the results of all of these function calls to
-- JSONB, as otherwise we cannot do equality comparisons.

SELECT plan(10);

-- json, json

SELECT is(
  json_concatenate('{"a": 1}'::json, '{"b": 2}'::json)::jsonb,
  '{"a": 1, "b": 2}'::jsonb,
  'json_concatenate(json, json)'
);

SELECT is(
  json_concatenate('{"a": 1, "b": 2, "c": 3}'::json, '{"d": [1, 2]}'::json)::jsonb,
  '{"a": 1, "b": 2, "c": 3, "d": [1, 2]}'::jsonb,
  'json_concatenate(json, json): non-simple object'
);

SELECT is(
  json_concatenate('{"a": 1}'::json, '{}'::json)::jsonb,
  '{"a": 1}'::jsonb,
  'json_concatenate(json, json): empty second argument'
);

SELECT is(
  json_concatenate('{}'::json, '{}'::json)::jsonb,
  '{}'::jsonb,
  'json_concatenate(json, json): both empty'
);

SELECT is(
  json_concatenate('{"a": 1}'::json, '{"a": 2}'::json)::jsonb,
  '{"a": 2}'::jsonb,
  'json_concatenate(json, json): update wins'
);

-- json, jsonb

SELECT is(
  json_concatenate('{"a": 1}'::json, '{"b": 2}'::jsonb)::jsonb,
  '{"a": 1, "b": 2}'::jsonb,
  'json_concatenate(json, jsonb)'
);

SELECT is(
  json_concatenate('{"a": 1, "b": 2, "c": 3}'::json, '{"d": [1, 2]}'::jsonb)::jsonb,
  '{"a": 1, "b": 2, "c": 3, "d": [1, 2]}'::jsonb,
  'json_concatenate(json, jsonb): non-simple object'
);

SELECT is(
  json_concatenate('{"a": 1}'::json, '{}'::jsonb)::jsonb,
  '{"a": 1}'::jsonb,
  'json_concatenate(json, jsonb): empty second argument'
);

SELECT is(
  json_concatenate('{}'::json, '{}'::jsonb)::jsonb,
  '{}'::jsonb,
  'json_concatenate(json, jsonb): both empty'
);

SELECT is(
  json_concatenate('{"a": 1}'::json, '{"a": 2}'::jsonb)::jsonb,
  '{"a": 2}'::jsonb,
  'json_concatenate(json, jsonb): update wins'
);


SELECT * FROM finish();
ROLLBACK;