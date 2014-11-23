from django.conf.urls import patterns, url

urlpatterns = patterns('dashboard.views',
                       url(r'^$', 'home_view', (), 'home'),
                       url(r'^category/(?P<slug>[\w-]+)/$', 'category_view', (), 'category'),
                       url(r'^visualization/(?P<slug>[\w-]+)/$', 'visualization_view', (), 'embedded_viz'),
                       )