import json

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.utils.html import conditional_escape as escape

from .models import Search

def uikit(request):
    searches = Search.objects.filter(term__matches='%s:*' % request.GET['search'].lower())

    return HttpResponse(json.dumps({
        'results': [
            {
                'title': escape(search.title),
                'url': reverse(search.url_name, kwargs=search.url_kwargs),
                'text': escape(search.detail),
            } for search in searches
        ]
    }))
