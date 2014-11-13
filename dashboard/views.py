from django.shortcuts import render_to_response
from django.template import RequestContext
from .models import Category, DataPoint


def home_view(request):
    context = {}

    data_points = DataPoint.objects.filter(featured=True).order_by('name')
    summary_data = [data_point.display_summary() for data_point in data_points]

    context['summary'] = sorted(summary_data, key=lambda item: item['latest_month']['date'], reverse=True)

    return render_to_response('home.html', context, context_instance=RequestContext(request))


def table_view(request):
    context = {}
    table_data = {}

    for category in Category.objects.all():
        data_points = DataPoint.objects.filter(category__name=category.name)
        table_data[category.name] = [data_point.display_data() for data_point in data_points]

    context['table'] = table_data

    return render_to_response('table.html', context, context_instance=RequestContext(request))


# from django.views.generic import TemplateView
#
#
# class HomeView(TemplateView):
#     template_name = 'home.html'

# context = {}
#
# for category in Category.objects.all():
#     data_points = DataPoint.objects.filter(category__name = category.name)
#     context[category.name] = [data_point.display_data() for data_point in data_points]