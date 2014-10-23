from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dashboard_gobernacion.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    (r'^', include('dashboard.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
)
