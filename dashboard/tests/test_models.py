from datetime import datetime
from django.test import TestCase
from dashboard.models import Category, DataPoint, EmbeddedVisualization
import responses
import json


class CategoryModelTest(TestCase):

    def test_get_absolute_url(self):
        category_ = Category()
        category_.name = 'Test category'
        category_.save()
        self.assertEqual(category_.get_absolute_url(), '/category/%s/' % (category_.slug,))


class DataPointModelTest(TestCase):

    test_data = '[{"total" : "6.534", "date" : "2014-12-01T00:00:00"}, ' \
                '{"total" : "5.855",  "date" : "2014-11-01T00:00:00"}, ' \
                '{"total" : "6.154",  "date" : "2014-10-01T00:00:00"}, ' \
                '{"total" : "6.409",  "date" : "2014-09-01T00:00:00"}, ' \
                '{"total" : "6.499",  "date" : "2014-08-01T00:00:00"}, ' \
                '{"total" : "5.95",  "date" : "2014-07-01T00:00:00"}, ' \
                '{"total" : "5.759",  "date" : "2014-06-01T00:00:00"}, ' \
                '{"total" : "6.671",  "date" : "2014-05-01T00:00:00"}, ' \
                '{"total" : "6.276",  "date" : "2014-04-01T00:00:00"}, ' \
                '{"total" : "6.142",  "date" : "2014-03-01T00:00:00"}, ' \
                '{"total" : "6.715",  "date" : "2014-02-01T00:00:00"}, ' \
                '{"total" : "6.359",  "date" : "2014-01-01T00:00:00"}, ' \
                '{"total" : "6.134",  "date" : "2013-12-01T00:00:00"}]'

    bad_test_data = '[{"total" : "6.534", "date" : "12-01-2014T00:00:00.00-04:00"}, ' \
                    '{"total" : "5.855",  "date" : "11-01-2014T00:00:00.00-04:00"}, ' \
                    '{"total" : "6.154",  "date" : "10-01-2014T00:00:00.00-04:00"}, ' \
                    '{"total" : "6.409",  "date" : "09-01-2014T00:00:00.00-04:00"}, ' \
                    '{"total" : "6.499",  "date" : "08-01-2014T00:00:00.00-04:00"}, ' \
                    '{"total" : "5.95",  "date" : "07-01-2014T00:00:00.00-04:00"}, ' \
                    '{"total" : "5.759",  "date" : "06-01-2014T00:00:00.00-04:00"}, ' \
                    '{"total" : "6.671",  "date" : "05-01-2014T00:00:00.00-04:00"}, ' \
                    '{"total" : "6.276",  "date" : "04-01-2014T00:00:00.00-04:00"}, ' \
                    '{"total" : "6.142",  "date" : "03-01-2014T00:00:00.00-04:00"}, ' \
                    '{"total" : "6.715",  "date" : "02-01-2014T00:00:00.00-04:00"}, ' \
                    '{"total" : "6.359",  "date" : "01-01-2014T00:00:00.00-04:00"}, ' \
                    '{"total" : "6.134",  "date" : "12-01-2013T00:00:00.00-04:00"}]'

    def test_check_previous_month_calc(self):
        latest_month = {'date': datetime.strptime('2015-04-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 0}
        previous_month = {'date': datetime.strptime('2015-03-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 1}
        result = DataPoint.check_previous_month(latest_month, previous_month)
        self.assertEquals(result['date'], datetime(2015, 3, 1, 0, 0))

    def test_check_month_last_year_calc(self):
        latest_month = {'date': datetime.strptime('2015-01-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 0}
        month_last_year = {'date': datetime.strptime('2014-01-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 1}
        result = DataPoint.check_month_last_year(latest_month, month_last_year)
        self.assertEquals(result['date'], datetime(2014, 1, 1, 0, 0))

    def test_check_percent_change_calc(self):
        latest_month_a = {'date': datetime.strptime('2015-04-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 240}
        month_last_year_a = {'date': datetime.strptime('2014-04-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 200}
        latest_month_b = {'date': datetime.strptime('2015-04-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 200}
        month_last_year_b = {'date': datetime.strptime('2014-04-01T00:00:00'[:10], '%Y-%m-%d'), 'value': 240}
        result_a = DataPoint.check_percent_change(float(latest_month_a['value']), float(month_last_year_a['value']))
        result_b = DataPoint.check_percent_change(float(latest_month_b['value']), float(month_last_year_b['value']))
        self.assertEquals(result_a, 20.0)
        self.assertEquals(result_b, -16.67)

    @responses.activate
    def test_get_data_ok(self):
        data_point_ = DataPoint()
        category_ = Category.objects.create()
        data_point_.category_id = category_.pk
        data_point_.name = 'Test Data Point'
        data_point_.resource = 'https://data.pr.gov/resource/abcd-1234.json'
        data_point_.date_field = 'date'
        data_point_.data_field = 'total'
        data_point_.save()

        responses.add(responses.GET, 'https://data.pr.gov/resource/abcd-1234.json',
                      body=self.test_data, status=200, content_type='application/json')

        r = DataPoint.get_data(data_point_, token={'access_token': '123abc'})

        self.assertEqual(200, r.status_code)
        self.assertEqual([{'date': '2014-12-01T00:00:00', 'total': '6.534'},
                          {'date': '2014-11-01T00:00:00', 'total': '5.855'},
                          {'date': '2014-10-01T00:00:00', 'total': '6.154'},
                          {'date': '2014-09-01T00:00:00', 'total': '6.409'},
                          {'date': '2014-08-01T00:00:00', 'total': '6.499'},
                          {'date': '2014-07-01T00:00:00', 'total': '5.95'},
                          {'date': '2014-06-01T00:00:00', 'total': '5.759'},
                          {'date': '2014-05-01T00:00:00', 'total': '6.671'},
                          {'date': '2014-04-01T00:00:00', 'total': '6.276'},
                          {'date': '2014-03-01T00:00:00', 'total': '6.142'},
                          {'date': '2014-02-01T00:00:00', 'total': '6.715'},
                          {'date': '2014-01-01T00:00:00', 'total': '6.359'},
                          {'date': '2013-12-01T00:00:00', 'total': '6.134'}], r.json())

    @responses.activate
    def test_get_data_error(self):
        data_point_ = DataPoint()
        category_ = Category.objects.create()
        data_point_.category_id = category_.pk
        data_point_.name = 'Test Data Point'
        data_point_.resource = 'https://data.pr.gov/resource/abcd-1234.json'
        data_point_.date_field = 'date'
        data_point_.data_field = 'total'
        data_point_.save()

        responses.add(responses.GET, 'https://data.pr.gov/resource/abcd-1234.json',
                      body=self.test_data, status=404, content_type='application/json')

        r = DataPoint.get_data(data_point_, token={'access_token': '123abc'})
        self.assertEqual(404, r['status_code'])
        self.assertEqual('Test Data Point', r['name'])

    @responses.activate
    def test_display_data_ok(self):
        data_point_ = DataPoint()
        category_ = Category.objects.create()
        data_point_.category_id = category_.pk
        data_point_.name = 'Test Data Point'
        data_point_.resource = 'https://data.pr.gov/resource/abcd-1234.json'
        data_point_.date_field = 'date'
        data_point_.data_field = 'total'
        data_point_.trend_upwards_positive = True
        data_point_.featured = True
        data_point_.save()

        responses.add(responses.GET, 'https://data.pr.gov/resource/abcd-1234.json',
                      body=self.test_data, status=200, content_type='application/json')

        r = DataPoint.display_data(data_point_, token={'access_token': '123abc'})
        self.assertEqual('Test Data Point', r['data'])
        self.assertEqual([{'date': datetime.strptime(x[data_point_.date_field][:10], '%Y-%m-%d'),
                           'value': x[data_point_.data_field]} for x in json.loads(self.test_data)], r['data_set'])
        self.assertEqual(datetime(2014, 12, 1, 0, 0), r['latest_month']['date'])
        self.assertEqual('6.534', r['latest_month']['value'])
        self.assertEqual(datetime(2014, 11, 1, 0, 0), r['previous_month']['date'])
        self.assertEqual('5.855', r['previous_month']['value'])
        self.assertEqual(datetime(2013, 12, 1, 0, 0), r['month_last_year']['date'])
        self.assertEqual('6.134', r['month_last_year']['value'])
        self.assertEqual(6.52, r['percent_change'])
        self.assertEqual(True, r['trend_direction'])
        self.assertEqual(True, r['trend_positive'])

    @responses.activate
    def test_display_data_date_error(self):
        data_point_ = DataPoint()
        category_ = Category.objects.create()
        data_point_.category_id = category_.pk
        data_point_.name = 'Test Data Point'
        data_point_.resource = 'https://data.pr.gov/resource/abcd-1234.json'
        data_point_.date_field = 'date'
        data_point_.data_field = 'total'
        data_point_.trend_upwards_positive = True
        data_point_.featured = True
        data_point_.save()

        responses.add(responses.GET, 'https://data.pr.gov/resource/abcd-1234.json',
                      body=self.bad_test_data, status=200, content_type='application/json')

        r = DataPoint.display_data(data_point_, token={'access_token': '123abc'})
        self.assertEqual('Incorrect date format', r)

    @responses.activate
    def test_display_summary_ok(self):
        data_point_ = DataPoint()
        category_ = Category.objects.create(name='Test Category')
        data_point_.category_id = category_.pk
        data_point_.name = 'Test Data Point'
        data_point_.resource = 'https://data.pr.gov/resource/abcd-1234.json'
        data_point_.date_field = 'date'
        data_point_.data_field = 'total'
        data_point_.trend_upwards_positive = True
        data_point_.featured = True
        data_point_.save()

        responses.add(responses.GET, 'https://data.pr.gov/resource/abcd-1234.json',
                      body=self.test_data, status=200, content_type='application/json')

        r = DataPoint.display_data(data_point_, token={'access_token': '123abc'})
        self.assertEqual('Test Data Point', r['data'])
        self.assertEqual(datetime(2014, 12, 1, 0, 0), r['latest_month']['date'])
        self.assertEqual('6.534', r['latest_month']['value'])
        self.assertEqual(6.52, r['percent_change'])
        self.assertEqual(True, r['trend_direction'])
        self.assertEqual(True, r['trend_positive'])
        self.assertEqual('Test Category', data_point_.category.name)

    @responses.activate
    def test_display_summary_date_error(self):
        data_point_ = DataPoint()
        category_ = Category.objects.create()
        data_point_.category_id = category_.pk
        data_point_.name = 'Test Data Point'
        data_point_.resource = 'https://data.pr.gov/resource/abcd-1234.json'
        data_point_.date_field = 'date'
        data_point_.data_field = 'total'
        data_point_.trend_upwards_positive = True
        data_point_.featured = True
        data_point_.save()

        responses.add(responses.GET, 'https://data.pr.gov/resource/abcd-1234.json',
                      body=self.bad_test_data, status=200, content_type='application/json')

        r = DataPoint.display_data(data_point_, token={'access_token': '123abc'})
        self.assertEqual('Incorrect date format', r)


class EmbeddedVisualizationModelTest(TestCase):

    def test_get_absolute_url(self):
        category_ = Category.objects.create()
        embedded_ = EmbeddedVisualization()
        embedded_.category_id = category_.pk
        embedded_.name = 'Visualization Test'
        embedded_.save()
        self.assertEquals(embedded_.get_absolute_url(), '/visualization/%s/' % (embedded_.slug,))