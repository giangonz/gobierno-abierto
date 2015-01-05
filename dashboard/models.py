# -*- coding: utf-8 -*-

from datetime import datetime
from django.utils.timezone import utc
import requests
from requests import HTTPError
from django.db import models
from django.core.urlresolvers import reverse


# Quick hack to see colors on cards
category_colors = {
    u'Desarrollo e Infraestructura': '#80cbc4',
    u'Transportación': '#e6ee9c',
    u'Turismo': '#ffe082',
    u'Economía y Finanzas': '#c5e1a5',
    u'Salud': '#ef9a9a',
    u'Educación': '#ffcc80',
    u'Negocios y Corporaciones': '#ffab91',
    u'Familia y Servicio Social': '#fff59d',
    u'Tecnologias': '#9fa8da',
    u'Permisos y Ambiente': '#a5d6a7',
    u'Seguridad Pública': '#b0bec5',
}

# Quick hack to see icons on cards
category_icons = {
    u'Desarrollo e Infraestructura': 'images/lightbulb.svg',
    u'Transportación': 'images/traffic-light.svg',
    u'Turismo': 'images/white-balance-sunny.svg',
    u'Economía y Finanzas': 'images/cash.svg',
    u'Salud': 'images/hospital.svg',
    u'Educación': 'images/school.svg',
    u'Negocios y Corporaciones': 'images/wallet-travel.svg',
    u'Familia y Servicio Social': 'images/human.svg ',
    u'Tecnologias': 'images/laptop.svg',
    u'Permisos y Ambiente': 'images/file-document-box.svg',
    u'Seguridad Pública': 'images/security.svg',
}


class BaseModel(models.Model):
    enabled = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_disabled = models.DateTimeField(blank=True, null=True)

    slug = models.SlugField(unique=True)

    def save(self):
        if not self.enabled:
            self.disabled_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(BaseModel, self).save()

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=100, verbose_name='category')

    def __unicode__(self):
        return u'%s' % self.name

    def get_icon(self):
        return category_icons[self.name]

    def get_color(self):
        return category_colors[self.name]

    def get_absolute_url(self):
        return reverse('category', args=[{"slug": self.slug}])

    class Meta:
        verbose_name = u'category'
        verbose_name_plural = u'categories'

# Future functionality: Sum, grouping...
# class Action(models.Model):
#     name = models.CharField(max_length=100, verbose_name='action')


class DataPoint(BaseModel):
    name = models.CharField(max_length=100, verbose_name='data point')
    category = models.ForeignKey('Category', verbose_name='category')
    resource = models.URLField(max_length=200)
    date_field = models.CharField(max_length=100, verbose_name='date field')
    data_field = models.CharField(max_length=100, verbose_name='data field')
    # action = models.ForeignKey('Action', verbose_name='action')
    # Is it a good thing that this stat went up? Unemployment went up? Bad! Labor participation went up? Good!
    # Used for stat color
    trend_upwards_positive = models.BooleanField(default=False, verbose_name='upward trend positive?')
    featured = models.BooleanField(default=False, verbose_name='featured set?')

    def __unicode__(self):
        return u'%s' % self.name

    def check_previous_month(self, latest_month, previous_month):
        if ((latest_month['date'].month-1) == previous_month['date'].month) and \
                (latest_month['date'].year == previous_month['date'].year):
            return previous_month
        else:
            return None

    def check_month_last_year(self, latest_month, month_last_year):
        if (latest_month['date'].month == month_last_year['date'].month) and \
                ((latest_month['date'].year-1) == month_last_year['date'].year):
            return month_last_year
        else:
            return None

    def check_percent_change(self, latest_month, month_last_year):
        change = latest_month - month_last_year

        percent_change = (change / month_last_year) * 100

        return round(percent_change, 2)

    def display_data(self, token):
        #Bring the current month plus year, for comparing and charting.
        try:

            data_request = '%s?$select=%s, %s&$order=%s DESC&$limit=13' % (self.resource, self.date_field,
                                                                           self.data_field, self.date_field)

            headers = {"content-type": "application/json", "Authorization": "OAuth " + token}

            r = requests.get(data_request, headers=headers)
            r.raise_for_status()

            data_set = [{'date': datetime.strptime(x[self.date_field][:10], '%Y-%m-%d'),
                         'value': x[self.data_field]} for x in r.json()]
            latest_month = data_set[0]
            previous_month = self.check_previous_month(latest_month, data_set[1])
            month_last_year = self.check_month_last_year(latest_month, data_set[-1])
            percent_change = self.check_percent_change(float(latest_month['value']), float(month_last_year['value']))
            trend_direction = True if percent_change > 0 else False
            trend_positive = True if self.trend_upwards_positive else False

            return {'data': self.name, 'data_set': data_set, 'latest_month': latest_month,
                    'previous_month': previous_month, 'month_last_year': month_last_year,
                    'category_color': category_colors[self.category.name],
                    'category_icon': category_icons[self.category.name], 'percent_change': abs(percent_change),
                    'trend_direction': trend_direction, 'trend_positive': trend_positive}

        except HTTPError as e:
            return e

    def display_summary(self, token):
        try:
            data_request = '%s?$select=%s, %s&$order=%s DESC&$limit=13' % (self.resource, self.date_field,
                                                                           self.data_field, self.date_field)

            headers = {"content-type": "application/json", "Authorization": "OAuth " + token}

            r = requests.get(data_request, headers=headers)
            r.raise_for_status()

            data_set = [{'date': datetime.strptime(x[self.date_field][:10], '%Y-%m-%d'),
                         'value': x[self.data_field]} for x in r.json()]
            latest_month = data_set[0]
            month_last_year = self.check_month_last_year(latest_month, data_set[-1])
            percent_change = self.check_percent_change(float(latest_month['value']), float(month_last_year['value']))
            # Trend direction - If going up, is True. If going down, is False.
            trend_direction = True if percent_change > 0 else False
            trend_positive = True if self.trend_upwards_positive else False
            # if trend_direction True and trend_positive True - positive stat going up (green up arrow)
            # if trend_direction False and trend_positive True - positive stat going down (red down arrow)
            # if trend_direction True and trend_positive False - negative stat going up (red up arrow)
            # if trend_direction False and trend_positive False - negative stat going down (green down arrow)

            return {'data': self.name, 'latest_month': latest_month, 'percent_change': abs(percent_change),
                    'trend_direction': trend_direction, 'trend_positive': trend_positive,
                    'category': self.category, 'category_color': category_colors[self.category.name],
                    'category_icon': category_icons[self.category.name]}

        except HTTPError as e:
            return e


class EmbeddedVisualization(BaseModel):
    name = models.CharField(max_length=100)
    category = models.ForeignKey('Category', verbose_name='category')
    embedded = models.TextField()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('embedded_viz', args=[{"slug": self.slug}])