# -*- coding: utf-8 -*-

from datetime import datetime
from django.utils.timezone import utc
from django.utils.text import slugify
import requests
from requests import HTTPError
from django.db import models
from django.core.urlresolvers import reverse


class BaseModel(models.Model):
    enabled = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_disabled = models.DateTimeField(blank=True, null=True)

    slug = models.SlugField(unique=True)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.enabled:
            self.disabled_date = datetime.utcnow().replace(tzinfo=utc)
        super(BaseModel, self).save()

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=100, verbose_name='category', blank=False, null=False)
    color = models.CharField(max_length=100, verbose_name='color', blank=False, null=False, default='#c0c0c0')
    icon = models.CharField(max_length=100, verbose_name='icon', blank=False, null=False, default='images/human.svg')

    def __str__(self):
        return u'%s' % self.name

    def get_color(self):
        return u'%s' % self.color

    def get_icon(self):
        return u'%s' % self.icon

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})

    def save(self, force_insert=False, force_update=False, using=None):
        self.slug = slugify(self.name, )
        super(Category, self).save()

    class Meta:
        verbose_name = u'category'
        verbose_name_plural = u'categories'

# Future functionality: Sum, grouping...
# class Action(models.Model):
#     name = models.CharField(max_length=100, verbose_name='action')


class DataPoint(BaseModel):
    name = models.CharField(max_length=100, verbose_name='data point', blank=False, null=False)
    category = models.ForeignKey('Category', verbose_name='category', blank=False, null=False)
    resource = models.URLField(max_length=200, blank=False, null=False)
    date_field = models.CharField(max_length=100, verbose_name='date field', blank=False, null=False)
    data_field = models.CharField(max_length=100, verbose_name='data field', blank=False, null=False)
    # action = models.ForeignKey('Action', verbose_name='action')
    # Is it a good thing that this stat went up? Unemployment went up? Bad! Labor participation went up? Good!
    # Used for stat color
    trend_upwards_positive = models.BooleanField(default=False, verbose_name='upward trend positive?',
                                                 blank=False, null=False)
    featured = models.BooleanField(default=False, verbose_name='featured set?', blank=False, null=False)

    def __str__(self):
        return u'%s' % self.name

    @staticmethod
    def check_previous_month(latest_month, previous_month):
        if ((latest_month['date'].month-1) == previous_month['date'].month) and \
                (latest_month['date'].year == previous_month['date'].year):
            return previous_month
        else:
            return None

    @staticmethod
    def check_month_last_year(latest_month, month_last_year):
        if (latest_month['date'].month == month_last_year['date'].month) and \
                ((latest_month['date'].year-1) == month_last_year['date'].year):
            return month_last_year
        else:
            return None

    @staticmethod
    def check_percent_change(latest_month, month_last_year):
        change = latest_month - month_last_year

        percent_change = (change / month_last_year) * 100

        return round(percent_change, 2)

    def get_data(self, token):
        try:
            data_request = '%s?$select=%s, %s&$order=%s DESC&$limit=13' % (self.resource, self.date_field,
                                                                           self.data_field, self.date_field)

            # headers = {"content-type": "application/json", "Authorization": "OAuth " + token['access_token']}
            headers = {"content-type": "application/json"}

            r = requests.get(data_request, headers=headers)
            r.raise_for_status()

            return r

        except HTTPError as e:
            status_code = e.response.status_code
            return {'status_code': status_code, 'name': self.name}

    def display_data(self, token):
        #Bring the current month plus year, for comparing and charting.
        try:

            data_request = self.get_data(token)

            data_set = [{'date': datetime.strptime(x[self.date_field][:10], '%Y-%m-%d'),
                         'value': x[self.data_field]} for x in data_request.json()]
            latest_month = data_set[0]
            previous_month = self.check_previous_month(latest_month, data_set[1])
            month_last_year = self.check_month_last_year(latest_month, data_set[-1])
            percent_change = self.check_percent_change(float(latest_month['value']), float(month_last_year['value']))
            trend_direction = True if percent_change > 0 else False
            trend_positive = True if self.trend_upwards_positive else False

            return {'data': self.name, 'data_set': data_set, 'latest_month': latest_month,
                    'previous_month': previous_month, 'month_last_year': month_last_year,
                    'category_color': self.category.color, 'category_icon': self.category.icon,
                    'percent_change': abs(percent_change), 'trend_direction': trend_direction,
                    'trend_positive': trend_positive}

        except ValueError:
            return {'error': ValueError('Incorrect date format'), 'name': self.name}
        except ArithmeticError:
            return {'error': ArithmeticError('Incorrect calculation'), 'name': self.name}
        except Exception:
            return {'error': 'Configuration error', 'name': self.name}

    def display_summary(self, token):
        try:

            data_request = self.get_data(token)

            data_set = [{'date': datetime.strptime(x[self.date_field][:10], '%Y-%m-%d'),
                         'value': x[self.data_field]} for x in data_request.json()]
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
                    'category': self.category, 'category_color': self.category.color,
                    'category_icon': self.category.icon}

        except ValueError:
            return {'error': ValueError('Incorrect date format'), 'name': self.name}
        except ArithmeticError:
            return {'error': ArithmeticError('Incorrect calculation'), 'name': self.name}
        except Exception:
            return {'error': 'Configuration error', 'name': self.name}


class EmbeddedVisualization(BaseModel):
    name = models.CharField(max_length=100, blank=False, null=False)
    category = models.ForeignKey('Category', verbose_name='category', blank=False, null=False)
    embedded = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('embedded_viz', kwargs={'slug': self.slug})

    def save(self, force_insert=False, force_update=False, using=None):
        self.slug = slugify(self.name, )
        super(EmbeddedVisualization, self).save()