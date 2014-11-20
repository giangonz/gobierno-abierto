from django.conf.urls import patterns, url

urlpatterns = patterns('dashboard.views',
                       url(r'^$', 'home_view', (), 'home'),
                       url(r'^category/(?P<slug>[\w-]+)/$', 'category_view', (), 'category'),
                       )