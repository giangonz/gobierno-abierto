from datetime import datetime
from django.core.exceptions import ValidationError
from django.test import TestCase
from dashboard.models import Category, DataPoint, EmbeddedVisualization


class CategoryModelTest(TestCase):

    def test_get_absolute_url(self):
        category_ = Category()
        category_.name = 'Test category'
        category_.save()
        self.assertEqual(category_.get_absolute_url(), '/category/%s/' % (category_.slug,))


class DataPointModelTest(TestCase):

    def test_check_previous_month_calc(self):
        latest_month = {'date': datetime.strptime('2015-04-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 0}
        previous_month = {'date': datetime.strptime('2015-03-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 1}
        # TODO fix this self reference
        result = DataPoint.check_previous_month(self, latest_month, previous_month)
        self.assertEquals(result['date'], datetime(2015, 3, 1, 0, 0))

    def test_check_month_last_year_calc(self):
        latest_month = {'date': datetime.strptime('2015-01-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 0}
        month_last_year = {'date': datetime.strptime('2014-01-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 1}
        # TODO fix this self reference
        result = DataPoint.check_month_last_year(self, latest_month, month_last_year)
        self.assertEquals(result['date'], datetime(2014, 1, 1, 0, 0))

    def test_check_percent_change_calc(self):
        latest_month_a = {'date': datetime.strptime('2015-04-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 240}
        month_last_year_a = {'date': datetime.strptime('2014-04-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 200}
        latest_month_b = {'date': datetime.strptime('2015-04-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 200}
        month_last_year_b = {'date': datetime.strptime('2014-04-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 240}
        # TODO fix this self reference
        result_a = DataPoint.check_percent_change(self, float(latest_month_a['value']), float(month_last_year_a['value']))
        result_b = DataPoint.check_percent_change(self, float(latest_month_b['value']), float(month_last_year_b['value']))
        self.assertEquals(result_a, 20.0)
        self.assertEquals(result_b, -16.67)

    def test_display_data(self):
        pass


class EmbeddedVisualizationModelTest(TestCase):

    def test_get_absolute_url(self):
        category_ = Category.objects.create()
        embedded_ = EmbeddedVisualization()
        embedded_.category_id = category_.pk
        embedded_.name = 'Visualization Test'
        embedded_.save()
        self.assertEquals(embedded_.get_absolute_url(), '/visualization/%s/' % (embedded_.slug,))