# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from models import Post, Tag, Comment
from django.db.models import Q
import md5, urllib, urllib2
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMessage

def by_slug(request, slug=''):
    post = get_object_or_404(Post, slug=slug)
    editable = request.user.is_authenticated() and request.user.is_staff
    if post.state == Post.HIDDEN and not editable:
        raise Http404
    comments = list(post.comments.all().order_by('date'))
    if (request.method == 'POST'):
        do_comment(request, post, request.POST, comments)
        post = get_object_or_404(Post, slug=slug)
    comment_count = len([comment for comment in comments if not comment.spam])
    return render(request, 'post.html', { 'post': post,
                                          'editable':editable,
                                          'title':post.title,
                                          'mathjax':True,
                                          'comments':comments,
                                          'comment_count':comment_count})

def isLegitEmail(email):
    return True
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def do_comment(request, post, attrs, all_comments=None):
    if not ('name' in attrs
            and 'text' in attrs
            and 'email' in attrs):
        return False
    if not all_comments:
        all_comments = post.comments.all()
    comment = Comment()
    comment.post = post
    comment.name = attrs['name']
    comment.text = attrs['text']
    comment.email = attrs['email']
    comment.spam = akismet_check(request, comment)
    comment.subscribed = attrs.get('subscribed', False)
    comment.save()
    all_comments.append(comment)
    if comment.spam:
        return # don't email people for spam comments!
    emails = {}
    for c in all_comments:
        if c.subscribed and c.email != comment.email and isLegitEmail(c.email):
            emails[c.email] = c.name
    template = get_template('comment_email.html')
    subject = "Someone replied to your comment"
    for email, name in emails.iteritems():
        text = template.render(Context({
                    'comment':comment,
                    'email':email,
                    'name':name
                    }))
        msg = EmailMessage(subject, text, "robot@benkuhn.net", [email])
        msg.content_subtype = 'html'
        msg.send()

def unsub(request, slug='', email=''):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(email=email).update(subscribed=False)
    return render(request, 'unsub.html', { 'title':'farewell' })

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def akismet_check(request, comment):
    if settings.AKISMET_KEY == '':
        return comment.name == 'viagra-test-123'
    params = {
        'blog'                 : request.build_absolute_uri('/'),
        'user_ip'              : get_client_ip(request),
        'user_agent'           : request.META.get('HTTP_USER_AGENT'),
        'referrer'             : request.META.get('HTTP_REFERER'),
        'permalink'            : comment.post.get_absolute_url(),
        'comment_type'         : 'comment',
        'comment_author'       : comment.name,
        'comment_author_email' : comment.email,
        'comment_content'      : comment.text,
        }
    url = 'http://' + settings.AKISMET_KEY + '.rest.akismet.com/1.1/comment-check'
    r = urllib2.urlopen(url, data=urllib.urlencode(params)).read()
    if 'true' == r:
        return True
    else:
        return False

def tag(request, slug='', page=0, title=''):
    postList = Post.objects.prefetch_related('tags').filter(state=Post.PUBLISHED).order_by('-datePosted')
    if page is None:
        page = 1
    if slug is not None:
        tag = get_object_or_404(Tag, slug=slug)
        title = 'posts tagged ' + tag.name
        postList = postList.filter(tags__slug=slug)
    paginator = Paginator(postList, 10)
    page = int(page) + 1
    if page > paginator.num_pages:
        raise Http404
    posts = paginator.page(page)
    if len(posts) == 0:
        raise Http404
    return render(request, 'tag.html', { 'posts':posts,
                                         'title':title })

def archive(request, page=0):
    return tag(request, slug=None, page=page, title='archive')

class RssFeed(Feed):
    title = "benkuhn.net"
    link = "/"
    feed_url = "/rss/"
    author_name = "Ben Kuhn"
    description = "New posts on benkuhn.net."
    description_template = "rsspost.html"
    ttl = 5

    def items(self):
        return Post.objects.filter(state=Post.PUBLISHED).prefetch_related('tags').order_by('-datePosted')[:10]

    def item_title(self, post):
        return post.title

    def item_description(self, post):
        return post.excerpt

    item_guid_is_permalink = False
    def item_guid(self, post):
        return md5.new(str(post.id)).hexdigest()

    def item_categories(self, post):
        return [tag.name for tag in post.tags.all()]

rss = RssFeed()

def queue(request):
    if not request.user.is_authenticated() and request.user.is_staff:
        raise Http404
    posts = Post.objects.filter(~Q(state=Post.PUBLISHED))
    postsByLength = posts.extra(select={'length':'Length(text)'}).order_by('-length')
    return render(request, 'queue.html', { 'posts':postsByLength, 'title':'queue' })
