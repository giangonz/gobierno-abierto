from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import MissingTokenError

from .models import Category, DataPoint, EmbeddedVisualization

from dashboard_gobernacion.settings import CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL

import logging


class SocrataAccessError(Exception):
    pass


class TokenMissingError(Exception):
    pass


def get_token(request):
    try:
        token = request.session.get('token', False)

        if not token:
            raise TokenMissingError('Token missing')

        return token

    except TokenMissingError:
        logging.error(TokenMissingError('Token missing'))
        raise


def home_view(request):
    try:
        # token = get_token(request)
        token = '123'

        context = {}
        clean_data = []

        data_points = DataPoint.objects.filter(featured=True).order_by('name')

        summary_data = [data_point.display_summary(token) for data_point in data_points]

        if 403 in summary_data:
            raise SocrataAccessError('Socrata 403 or 404 Access Error')

        for i in summary_data:
            if 'error' in i:
                messages.add_message(request, messages.WARNING, '%s for %s data point, please correct' % (i['error'],
                                                                                                          i['name']))
            else:
                clean_data.append(i)

        context['summary'] = sorted(clean_data, key=lambda item: item['latest_month']['date'], reverse=True)

        return render_to_response('home.html', context, context_instance=RequestContext(request))

    except TokenMissingError:
        return redirect('authorize')
    except SocrataAccessError:
        logging.error(SocrataAccessError)
        return redirect('authorize')


def category_view(request, slug):
    try:
        # token = get_token(request)
        token = '123'

        context = {}
        table_data = {}
        clean_data = []

        category = Category.objects.get(slug=slug)

        data_points = DataPoint.objects.filter(category__id=category.pk).order_by('name')
        category = Category.objects.get(pk=category.pk)
        context['category'] = category

        category_data = [data_point.display_data(token) for data_point in data_points]

        for i in category_data:
            if 'error' in i:
                messages.add_message(request, messages.WARNING, '%s for %s data point, please correct' % (i['error'],
                                                                                                          i['name']))
            else:
                clean_data.append(i)

        table_data[category.name] = clean_data
        context['table'] = table_data

        return render_to_response('table.html', context, context_instance=RequestContext(request))

    except TokenMissingError:
        return redirect('authorize')


def category_visualization_view(request, slug):

    context = {}

    category = Category.objects.get(slug=slug)
    context['category'] = category

    category_viz = EmbeddedVisualization.objects.filter(category=category).order_by('name')
    context['category_visualization'] = category_viz

    return render_to_response('embedded_visualizations_list.html', context, context_instance=RequestContext(request))


def visualization_view(request, slug):

    context = {}

    viz = EmbeddedVisualization.objects.get(slug=slug)

    context['visualization'] = viz

    return render_to_response('embedded_visualization.html', context, context_instance=RequestContext(request))


def socrata_authorize_view(request):
    redirect_uri = request.build_absolute_uri(reverse('callback'))

    oauth = OAuth2Session(CLIENT_ID, redirect_uri=redirect_uri)
    authorization_url, state = oauth.authorization_url(AUTHORIZE_URL)

    return redirect(authorization_url)


def socrata_callback_view(request):
    state = request.GET.get('state')
    code = request.GET.get('code')

    if not code:
        raise Http404

    oauth2 = OAuth2Session(CLIENT_ID, state=state)

    try:
        token = oauth2.fetch_token(token_url=TOKEN_URL, client_secret=CLIENT_SECRET, code=code)
        request.session['token'] = token
    except MissingTokenError:
        return redirect('authorize')

    return redirect('home')