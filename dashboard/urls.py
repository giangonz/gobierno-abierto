from django.conf.urls import patterns, url

urlpatterns = patterns('dashboard.views',
                       url(r'^$', 'home_view', (), 'home'),
                       url(r'^table/', 'table_view', (), 'table'),
                       )