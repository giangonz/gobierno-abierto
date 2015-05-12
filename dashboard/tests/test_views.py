from importlib import import_module
from mock import Mock

from django.conf import settings
from django.test import TestCase

from dashboard.views import TokenMissingError, get_token
from dashboard.models import Category, EmbeddedVisualization


class HomeViewTest(TestCase):

    def setUp(self):
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

    def test_home_view_page_renders_template(self):
        session = self.session
        session['token'] = 'abc123'
        session.save()
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_get_token_missing_error(self):
        mock_request = Mock()
        mock_request.session = {}
        with self.assertRaises(TokenMissingError):
            get_token(mock_request)

    def test_home_view_page_redirect(self):
        response = self.client.get('/')
        self.assertRedirects(response, expected_url='/authorize/', target_status_code=302)


class CategoryViewTest(TestCase):

    def setUp(self):
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

    def test_category_view_page_renders_template(self):
        category_ = Category()
        category_.name = 'Test category'
        category_.save()

        session = self.session
        session['token'] = 'abc123'
        session.save()
        response = self.client.get('/category/%s/' % category_.slug)
        self.assertTemplateUsed(response, 'table.html')

    def test_category_get_token_missing_error(self):
        mock_request = Mock()
        mock_request.session = {}
        with self.assertRaises(TokenMissingError):
            get_token(mock_request)

    def test_category_view_page_redirect(self):
        response = self.client.get('/')
        self.assertRedirects(response, expected_url='/authorize/', target_status_code=302)


class CategoryVisualizationTest(TestCase):

    def test_category_visualization_view_render_template(self):
        category_ = Category()
        category_.name = 'Test category'
        category_.save()

        response = self.client.get('/category_visualizations/%s/' % category_.slug)
        self.assertTemplateUsed(response, 'embedded_visualizations_list.html')


class VisualizationTest(TestCase):

    def test_visualization_view_render_template(self):
        category_ = Category()
        category_.name = 'Test category'
        category_.save()
        embedded_ = EmbeddedVisualization()
        embedded_.category_id = category_.pk
        embedded_.name = 'Visualization Test'
        embedded_.save()

        response = self.client.get('/visualization/%s/' % embedded_.slug)
        self.assertTemplateUsed(response, 'embedded_visualization.html')