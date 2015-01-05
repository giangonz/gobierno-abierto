from django.conf.urls import patterns, url

urlpatterns = patterns('dashboard.views',
                       url(r'^$', 'home_view', (), 'home'),
                       url(r'^category/(?P<slug>[\w-]+)/$', 'category_view', (), 'category'),
                       url(r'^category_visualizations/(?P<slug>[\w-]+)/$', 'category_visualization_view', (),
                           'embedded_viz_list'),
                       url(r'^visualization/(?P<slug>[\w-]+)/$', 'visualization_view', (), 'embedded_viz'),
                       url(r'^authorize/$', 'socrata_authorize_view', (), 'authorize'),
                       url(r'^callback/$', 'socrata_callback_view', (), 'callback'),
                       )