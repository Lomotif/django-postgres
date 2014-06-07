from django.db import connection

SET_USER = """DO $$
BEGIN
  CREATE TEMP TABLE "_app_user" (user_id integer, ip_address inet);
  INSERT INTO _app_user VALUES (%(user)s, '%(host)s');
EXCEPTION WHEN OTHERS THEN
  UPDATE _app_user SET user_id=%(user)s, ip_address='%(host)s';
END;
$$;
"""

class AuditAppUserMiddleware(object):
    def process_view(self, request, *args, **kwargs):
        cursor = connection.cursor()
        if request.user.pk and request.META.get('REMOTE_ADDR'):
            cursor.execute(SET_USER % {
                'user': request.user.pk,
                'host': request.META['REMOTE_ADDR']
            })