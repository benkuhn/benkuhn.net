from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import posts.urls

admin.autodiscover()

pset = [
    url(r'^$', 'bknet.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/img/favicon.ico'}),
    url(r'^tag/(?P<slug>[\w-]+)/(?P<page>\d+)/$', 'posts.views.tag'),
    url(r'^rss/(?P<tag>[\w-]*)$', 'posts.views.rss'),
    url(r'^email/$', 'posts.views.email'),
    url(r'^subscribers/$', 'posts.views.subscribers'),
    url(r'^unsub/(?P<email>.+)$', 'posts.views.global_unsub'),
    url(r'^blog/(?P<page>\d+)/$', 'posts.views.blog'),
    url(r'^(?P<slug>[\w-]+)$', 'posts.views.by_slug'),
    url(r'^edit/(?P<slug>[\w-]+)$', 'posts.views.edit_by_slug'),
    url(r'^sendmail/(?P<slug>[\w-]+)$', 'posts.views.send_emails'),
    url(r'^q/$', 'posts.views.queue'),
    url(r'^unsub/(?P<slug>[\w-]+)/(?P<email>.+)$', 'posts.views.unsub'),
    url(r'^preview/$', 'posts.views.preview'),
    url(r'^.well-known/keybase.txt$', 'bknet.views.keybase'),
    url(r'^bestof/$', 'django.views.generic.simple.redirect_to', {'url': '/more/'}),
    url(r'^collected/(?P<tags>[\w,-]*)$', 'posts.views.collect'),
    # redirects for compatibility reasons
    url(r'^archive/(?P<page>\d+)/$', 'django.views.generic.simple.redirect_to', {'url':'/blog/%(page)s/'}),
    ]
for name in ['contact', 'projects', 'privacy', 'about', 'more']:
    pset.append(url(r'^' + name + '/$', 'bknet.views.' + name, name=name))

urlpatterns = patterns('', *pset
    # url(r'^bknet/', include('bknet.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)

urlpatterns += staticfiles_urlpatterns()
