# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.syndication.views import Feed
from models import Post, Tag

def by_slug(request, slug=''):
    post = get_object_or_404(Post, slug=slug)
    return render_to_response('post.html', { 'post': post })

def tag():
    pass # stub

def archive():
    pass # stub

class RssFeed(Feed):
    title = "benkuhn.net"
    link = "/posts/rss/"
    description = "New posts on benkuhn.net."
    description_template = "rsspost.html"

    def items(self):
        return Post.objects.order_by('-datePosted')[:10]

    def item_title(self, post):
        return post.title

    def item_description(self, post):
        return post.excerpt

rss = RssFeed()
