from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^tag/(?P<slug>[\w-]+)$', 'posts.views.tag'),
                       url(r'^rss/$', 'posts.views.rss'),
                       url(r'^archive/(?P<page>\d+)$', 'posts.views.archive'),
                       url(r'^(?P<slug>[\w-]+)$', 'posts.views.by_slug'),
                       url(r'^q/$', 'posts.views.queue'),
                       )
