-- We will store the audit trigger function in a schema: this means we
-- will always be able to refer to it regardless of the search path.

CREATE SCHEMA IF NOT EXISTS __audit;

CREATE OR REPLACE FUNCTION __audit.if_modified_func() RETURNS TRIGGER AS $body$
DECLARE
    excluded_cols TEXT[] = ARRAY[]::TEXT[];
    r record;
    row_data jsonb;
    changed_fields jsonb;
    
    app_user_id INTEGER;
    app_ip_address inet;
    client_query TEXT;
    statement_only BOOLEAN = 'f';
BEGIN
    IF TG_WHEN <> 'AFTER' THEN
        RAISE EXCEPTION '__audit.if_modified_func() may only run as an AFTER trigger';
    END IF;
    
    -- Inject the data from the _app_user table if it exists.
    BEGIN
      FOR r IN SELECT * FROM _app_user LIMIT 1 LOOP
          app_user_id = r.user_id;
          app_ip_address = r.ip_address;
      END LOOP;
    EXCEPTION WHEN OTHERS THEN
    END;
    
    IF TG_ARGV[0]::boolean IS DISTINCT FROM 'f'::boolean THEN
      client_query = current_query();
    ELSE
      client_query = NULL;
    END IF;

    IF TG_ARGV[1] IS NOT NULL THEN
        excluded_cols = TG_ARGV[1]::text[];
    END IF;
    
    IF (TG_OP = 'UPDATE' AND TG_LEVEL = 'ROW') THEN
        -- Convert our table to a json structure.
        row_data = to_json(OLD.*);
        -- Remove any columns we want to exclude, and then any
        -- columns that still have the same value as before the update.
        changed_fields =  to_json(NEW.*) - excluded_cols - row_data;
        IF changed_fields = '{}'::jsonb THEN
            -- All changed fields are ignored. Skip this update.
            RETURN NULL;
        END IF;
    ELSIF (TG_OP = 'DELETE' AND TG_LEVEL = 'ROW') THEN
        row_data = to_json(OLD.*) - excluded_cols;
    ELSIF (TG_OP = 'INSERT' AND TG_LEVEL = 'ROW') THEN
        row_data = to_json(NEW.*) - excluded_cols;
    ELSIF (TG_LEVEL = 'STATEMENT' AND TG_OP IN ('INSERT','UPDATE','DELETE','TRUNCATE')) THEN
        statement_only = 't';
    ELSE
        RAISE EXCEPTION '[__audit.if_modified_func] - Trigger func added as trigger for unhandled case: %, %',TG_OP, TG_LEVEL;
        RETURN NULL;
    END IF;
    INSERT INTO audit_auditlog (
      "action", "table_name",
      "timestamp", "transaction_id",
      "client_query", "statement_only",
      "row_data", "changed_fields",
      "app_user_id", "app_ip_address"
    ) VALUES (
      substring(TG_OP, 1, 1), TG_TABLE_NAME::text,
      current_timestamp, txid_current(),
      client_query, statement_only,
      row_data, changed_fields,
      app_user_id, app_ip_address
    );
    RETURN NULL;
END;
$body$
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public;

COMMENT ON FUNCTION __audit.if_modified_func() IS $body$
Track changes to a table at the statement and/or row level.

Optional parameters to trigger in CREATE TRIGGER call:

param 0: boolean, whether to log the query text. Default 't'.

param 1: text[], columns to ignore in updates. Default [].

         Updates to ignored cols are omitted from changed_fields.

         Updates with only ignored cols changed are not inserted
         into the audit log.

         Almost all the processing work is still done for updates
         that ignored. If you need to save the load, you need to use
         WHEN clause on the trigger instead.

         No warning or error is issued if ignored_cols contains columns
         that do not exist in the target table. This lets you specify
         a standard set of ignored columns.

There is no parameter to disable logging of values. Add this trigger as
a 'FOR EACH STATEMENT' rather than 'FOR EACH ROW' trigger if you do not
want to log row values.

Note that the user name logged is the login role for the session. The audit trigger
cannot obtain the active role because it is reset by the SECURITY DEFINER invocation
of the audit trigger its self.

If a (temporary, probably) table exists called _app_user, then this will supply
a user_id and ip_address that will be added to the log. This allows for you
to associate events with application level, rather than database users.
$body$;