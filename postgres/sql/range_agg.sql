CREATE OR REPLACE FUNCTION normalize(int4range[])
RETURNS int4range[] AS $$

DECLARE
  _range int4range;
  _current int4range;
  _agg_range int4range[];

BEGIN

  IF cardinality($1) < 2 THEN
    RETURN $1;
  END IF;

  _current := (SELECT x FROM unnest($1) x ORDER BY x LIMIT 1);
  _agg_range := ARRAY[_current];

  FOR _range IN SELECT unnest($1) x ORDER BY x LOOP
    IF _range && _current OR _range -|- _current THEN
      _agg_range := array_replace(_agg_range, _current, _current + _range);
      _current := _current + _range;
    ELSE
      _agg_range := array_append(_agg_range, _range);
      _current := _range;
    END IF;
  END LOOP;

  RETURN _agg_range;
END;

$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION missing_ranges(int4range[])
RETURNS int4range[] AS $$

DECLARE
  _range int4range;
  _missing int4range[];

BEGIN
  _missing := (SELECT
    array_agg(int4range(upper, lead, '[)'))
    FROM (
      SELECT lower(x), upper(x), lead(lower(x)) OVER (ORDER BY lower(x) NULLS FIRST)
      FROM unnest($1) x ORDER BY lower NULLS FIRST
    ) x
    WHERE upper < lead OR (lead IS NULL AND upper IS NOT NULL)
  );

  _range := (SELECT x FROM unnest($1) x ORDER BY x LIMIT 1);
  IF NOT lower_inf(_range) THEN
    _missing := array_prepend(int4range(NULL, lower(_range), '[)'), _missing);
  END IF;

  RETURN _missing;
END;

$$ LANGUAGE plpgsql;


CREATE AGGREGATE missing_ranges (int4range) (
  sfunc = array_append,
  stype = int4range[],
  finalfunc = missing_ranges
);