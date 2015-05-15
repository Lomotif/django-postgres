BEGIN;

SELECT plan(10);

-- json, json

SELECT is(
  jsonb_concatenate('{"a": 1}'::jsonb, '{"b": 2}'::json),
  '{"a": 1, "b": 2}'::jsonb,
  'jsonb_concatenate(jsonb, json)'
);

SELECT is(
  jsonb_concatenate('{"a": 1, "b": 2, "c": 3}'::jsonb, '{"d": [1, 2]}'::json),
  '{"a": 1, "b": 2, "c": 3, "d": [1, 2]}'::jsonb,
  'jsonb_concatenate(jsonb, json): non-simple object'
);

SELECT is(
  jsonb_concatenate('{"a": 1}'::jsonb, '{}'::json),
  '{"a": 1}'::jsonb,
  'jsonb_concatenate(jsonb, json): empty second argument'
);

SELECT is(
  jsonb_concatenate('{}'::jsonb, '{}'::json),
  '{}'::jsonb,
  'jsonb_concatenate(jsonb, json): both empty'
);

SELECT is(
  jsonb_concatenate('{"a": 1}'::jsonb, '{"a": 2}'::json),
  '{"a": 2}'::jsonb,
  'jsonb_concatenate(jsonb, json): update wins'
);

-- json, jsonb

SELECT is(
  jsonb_concatenate('{"a": 1}'::jsonb, '{"b": 2}'::jsonb),
  '{"a": 1, "b": 2}'::jsonb,
  'jsonb_concatenate(jsonb, jsonb)'
);

SELECT is(
  jsonb_concatenate('{"a": 1, "b": 2, "c": 3}'::jsonb, '{"d": [1, 2]}'::jsonb),
  '{"a": 1, "b": 2, "c": 3, "d": [1, 2]}'::jsonb,
  'jsonb_concatenate(jsonb, jsonb): non-simple object'
);

SELECT is(
  jsonb_concatenate('{"a": 1}'::jsonb, '{}'::jsonb),
  '{"a": 1}'::jsonb,
  'jsonb_concatenate(jsonb, jsonb): empty second argument'
);

SELECT is(
  jsonb_concatenate('{}'::jsonb, '{}'::jsonb),
  '{}'::jsonb,
  'jsonb_concatenate(jsonb, jsonb): both empty'
);

SELECT is(
  jsonb_concatenate('{"a": 1}'::jsonb, '{"a": 2}'::jsonb),
  '{"a": 2}'::jsonb,
  'jsonb_concatenate(jsonb, jsonb): update wins'
);


SELECT * FROM finish();
ROLLBACK;