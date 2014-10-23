from datetime import datetime
import requests
from requests import HTTPError
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='category')

# Future functionality: Sum, grouping...
# class Action(models.Model):
#     name = models.CharField(max_length=100, verbose_name='action')

    def __str__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = u'category'
        verbose_name_plural = u'categories'


class DataPoint(models.Model):
    name = models.CharField(max_length=100, verbose_name='data point')
    category = models.ForeignKey('Category', verbose_name='category')
    resource = models.URLField(max_length=200)
    date_field = models.CharField(max_length=100, verbose_name='date field')
    data_field = models.CharField(max_length=100, verbose_name='data field')
    # action = models.ForeignKey('Action', verbose_name='action')
    # Is it a good thing that this stat went up? Unemployment went up? Bad! Labor participation went up? Good!
    # Used for stat color
    up_good = models.BooleanField(default=False)

    def __str__(self):
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

    def display_data(self):
        #Bring the current month plus year, for comparing and charting.
        try:
            data_request = '%s?$select=%s, %s&$order=%s DESC&$limit=13' % (self.resource, self.date_field,
                                                                           self.data_field, self.date_field)
            r = requests.get(data_request)
            r.raise_for_status()

            data_set = [{'date': datetime.strptime(x[self.date_field][:10], '%Y-%m-%d'),
                         'value': x[self.data_field]} for x in r.json()]
            latest_month = data_set[0]
            previous_month = self.check_previous_month(latest_month, data_set[1])
            month_last_year = self.check_month_last_year(latest_month, data_set[-1])

            return {'data': self.name, 'data_set': data_set, 'latest_month': latest_month,
                    'previous_month': previous_month, 'month_last_year': month_last_year}

        except HTTPError as e:
            return e