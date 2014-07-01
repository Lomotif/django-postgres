import json

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.utils.html import conditional_escape as escape

from ..views import FormListView, AjaxTemplateMixin
from .models import Search
from .forms import SearchForm

def uikit(request):
    searches = Search.objects.matches(request.GET['search'])

    return HttpResponse(json.dumps({
        'results': [
            {
                'title': escape(search.title),
                'url': reverse(search.url_name, kwargs=search.url_kwargs),
                'text': escape(search.detail),
            } for search in searches
        ]
    }))



class SearchResults(AjaxTemplateMixin, FormListView):
    form_class = SearchForm
    context_object_name = 'search_results'
    paginate_by = 25

results = SearchResults.as_view(template_name='search/page.html', ajax_template_name='search/form.html')