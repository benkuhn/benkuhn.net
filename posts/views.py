# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from models import Post, Tag
from django.db.models import Q

def by_slug(request, slug=''):
    post = get_object_or_404(Post.objects.prefetch_related('tags'), slug=slug)
    editable = request.user.is_authenticated() and request.user.is_staff
    if not (post.published or editable):
        raise Http404
    if request.method == 'POST' and editable:
        form = PostForm()
    return render(request, 'post.html', { 'post': post,
                                          'editable':editable,
                                          'title':post.title,
                                          'mathjax':True })

def tag(request, slug='', page=0):
    postList = Post.objects.prefetch_related('tags').filter(published=True).order_by('-datePosted')
    if page is None:
        page = 1
    if slug is None:
        title = 'archive'
    else:
        tag = get_object_or_404(Tag, slug=slug)
        title = 'posts tagged ' + tag.name
        postList = postList.filter(tags__slug=slug)
    paginator = Paginator(postList, 10)
    posts = paginator.page(page)
    if len(posts) == 0:
        raise Http404
    return render(request, 'tag.html', { 'posts':posts,
                                         'title':title })

def archive(request, page=0):
    return tag(request, slug=None, page=page)

class RssFeed(Feed):
    title = "benkuhn.net"
    link = "/archive/1/"
    feed_url = "/rss/"
    author_name = "Ben Kuhn"
    description = "New posts on benkuhn.net."
    description_template = "rsspost.html"
    ttl = 5

    def items(self):
        return Post.objects.filter(published=True).prefetch_related('tags').order_by('-datePosted')[:10]

    def item_title(self, post):
        return post.title

    def item_description(self, post):
        return post.excerpt

    item_guid_is_permalink = False
    def item_guid(self, post):
        return md5.new(post.id).hexdigest()

    def item_categories(self, post):
        return [tag.name for tag in post.tags.all()]

rss = RssFeed()

def queue(request):
    if not request.user.is_authenticated() and request.user.is_staff:
        raise Http404
    posts = Post.objects.filter(published=False)
    return render(request, 'queue.html', { 'posts':posts, 'title':'queue' })
