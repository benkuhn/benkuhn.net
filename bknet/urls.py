from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import posts.urls

admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
pset = [
    url(r'^$', 'bknet.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^posts/', include(posts.urls)),
    url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/img/favicon.ico'}),
    ]
for name in ['contact', 'projects', 'other']:
    pset.append(url(r'^' + name + '/$', 'bknet.views.' + name, name=name))

urlpatterns = patterns('', *pset
    # url(r'^bknet/', include('bknet.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)

urlpatterns += staticfiles_urlpatterns()
