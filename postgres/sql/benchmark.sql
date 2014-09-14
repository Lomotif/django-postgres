--
-- Benchmark sql functions
--
-- Usage:
--
-- SELECT * FROM BENCHMARK(10000,
--   'to_json(''{}''::json)',
--   'to_json(''{}''::jsonb)'
-- );
--
-- Example output:
--
--          code         |  runtime   | corrected
-- ----------------------+------------+------------
--  [Control]            | 0.00612307 |          0
--  to_json('{}'::json)  |   0.012506 | 0.00638294
--  to_json('{}'::jsonb) |   0.013397 | 0.00727391
-- (3 rows)


DROP TYPE _benchmark CASCADE;

CREATE TYPE _benchmark AS (
    code      text,
    runtime   real,
    corrected real
);

CREATE OR REPLACE FUNCTION benchmark(n INTEGER, VARIADIC funcs TEXT[])
RETURNS SETOF _benchmark AS $$
DECLARE
    code TEXT := '';
    a    _benchmark;
BEGIN
    -- Start building the custom benchmarking function.
    code := $_$
        CREATE OR REPLACE FUNCTION _bench(n INTEGER)
        RETURNS SETOF _benchmark AS $__$
        DECLARE
            s TIMESTAMP;
            e TIMESTAMP;
            a RECORD;
            d numeric;
            res numeric;
            ret _benchmark;
        BEGIN
            -- Create control.
            s := timeofday();
            FOR a IN SELECT TRUE FROM generate_series( 1, $_$ || n || $_$ )
            LOOP
            END LOOP;
            e := timeofday();
            d := extract(epoch from e) - extract(epoch from s);
            ret := ROW( '[Control]', d, 0 );
            RETURN NEXT ret;

$_$;
    -- Append the code to bench each function call.
    FOR i IN array_lower(funcs,1) .. array_upper(funcs, 1) LOOP
        code := code || '
            s := timeofday();
            FOR a IN SELECT ' || funcs[i] || ' FROM generate_series( 1, '
                || n || $__$ ) LOOP
            END LOOP;
            e := timeofday();
            res := extract(epoch from e) - extract(epoch from s);
            ret := ROW(
                $__$ || quote_literal(funcs[i]) || $__$,
                res,
                res - d
            );
            RETURN NEXT ret;
$__$;
    END LOOP;

    -- Create the function.
    execute code || $_$
        END;
        $__$ language plpgsql;
$_$;

    -- Now execute the function.
    FOR a IN EXECUTE 'SELECT * FROM _bench(' || n || ')' LOOP
        RETURN NEXT a;
    END LOOP;

    -- Drop the function.
    DROP FUNCTION _bench(integer);
    RETURN;
END;
$$ language 'plpgsql';