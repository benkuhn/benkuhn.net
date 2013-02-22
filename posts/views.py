# Create your views here.
from django.shortcuts import render, render_to_response, get_object_or_404
from django.contrib.syndication.views import Feed
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from models import Post, Tag

def by_slug(request, slug=''):
    post = get_object_or_404(Post.objects.prefetch_related('tags'), slug=slug)
    editable = request.user.is_authenticated() and request.user.is_staff
    if not (post.published or editable):
        raise Http404
    if request.method == 'POST' and editable:
        form = PostForm()
    return render_to_response('post.html', { 'post': post,
                                             'editable':editable,
                                             'title':post.title })

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
    return render_to_response('tag.html', { 'posts':posts,
                                            'title':title })

def archive(request, page=0):
    return tag(request, slug=None, page=page)

class RssFeed(Feed):
    title = "benkuhn.net"
    link = "/posts/rss/"
    description = "New posts on benkuhn.net."
    description_template = "rsspost.html"

    def items(self):
        return Post.objects.filter(published=True).order_by('-datePosted')[:10]

    def item_title(self, post):
        return post.title

    def item_description(self, post):
        return post.excerpt

rss = RssFeed()

@staff_member_required
def queue(request):
    posts = Post.objects.filter(published=False)
    return render(request, 'queue.html', { 'posts':posts, 'title':'queue' })
