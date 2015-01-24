BEGIN;

SELECT plan(14);

SELECT is(
  json_subtract('{}'::json, '{}'::json)::jsonb,
  '{}'::jsonb,
  'json_subtract(json, json): both objects empty'
);

SELECT is(
  json_subtract('{"a": 1}'::json, '{}'::json)::jsonb,
  '{"a": 1}'::jsonb,
  'json_subtract(json, json): remove object empty'
);

SELECT is(
  json_subtract('{"a": 1}'::json, 'a'::text)::jsonb,
  '{}'::jsonb,
  'json_subtract(json, text): match found'
);

SELECT is(
  json_subtract('{"a": 1, "b": 2}'::json, 'a'::text)::jsonb,
  '{"b": 2}'::jsonb,
  'json_subtract(json, text): match found, other kept'
);

SELECT is(
  json_subtract('{"a": 1}'::json, 'b'::text)::jsonb,
  '{"a": 1}'::jsonb,
  'json_subtract(json, text): match not found'
);

SELECT is(
  json_subtract('{"a": 1, "b": 2}'::json, '{b}'::text[])::jsonb,
  '{"a": 1}'::jsonb,
  'json_subtract(json, text[]): one match found'
);

SELECT is(
  json_subtract('{"a": 1, "b": 2}'::json, '{b,a}'::text[])::jsonb,
  '{}'::jsonb,
  'json_subtract(json, text[]): both matches found'
);

SELECT is(
  json_subtract('{"a": 1, "b": 2}'::json, '{b,c}'::text[])::jsonb,
  '{"a": 1}'::jsonb,
  'json_subtract(json, text[]): one match found'
);

SELECT is(
  json_subtract('{"a": 1, "b": 2}'::json, '{c}'::text[])::jsonb,
  '{"a": 1, "b": 2}'::jsonb,
  'json_subtract(json, text[]): no matches found'
);

SELECT is(
  json_subtract('{"a": 1, "b": 2}'::json, '["b"]'::json)::jsonb,
  '{"a": 1}'::jsonb,
  'json_subtract(json, json): remove is json array: one match found'
);

SELECT is(
  json_subtract('{"a": 1, "b": 2}'::json, '["b","a"]'::json)::jsonb,
  '{}'::jsonb,
  'json_subtract(json, text[]): remove is json array: both matches found'
);

SELECT is(
  json_subtract('{"a": 1, "b": 2}'::json, '["b","c"]'::json)::jsonb,
  '{"a": 1}'::jsonb,
  'json_subtract(json, text[]): remove is json array: one match found'
);

SELECT is(
  json_subtract('{"a": 1, "b": 2}'::json, '["c"]'::json)::jsonb,
  '{"a": 1, "b": 2}'::jsonb,
  'json_subtract(json, text[]): remove is json array: no matches found'
);


SELECT is(
  ('{"a": 1}'::json - '{}'::json)::jsonb,
  '{"a": 1}'::jsonb,
  'json - json: second operand empty'
);


SELECT * FROM finish();
ROLLBACK;