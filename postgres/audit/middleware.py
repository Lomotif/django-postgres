from django.db import connection

SET_USER = """
CREATE TEMP TABLE IF NOT EXISTS "_app_user" (user_id integer, ip_address inet);
UPDATE _app_user SET user_id=%(user)s, ip_address='%(host)s';
INSERT INTO _app_user (user_id, ip_address) 
    SELECT %(user)s, '%(host)s' WHERE NOT EXISTS (SELECT * FROM _app_user);
"""

class AuditAppUserMiddleware(object):
    def process_view(self, request, *args, **kwargs):
        cursor = connection.cursor()
        if request.user.pk and request.META.get('REMOTE_ADDR'):
            cursor.execute(SET_USER % {
                'user': request.user.pk,
                'host': request.META['REMOTE_ADDR']
            })