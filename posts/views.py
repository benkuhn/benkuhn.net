# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from models import Post, Tag, Comment
from django.db.models import Q
import md5, urllib, urllib2, hashlib
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMessage
import md

def by_slug(request, slug=''):
    post = get_object_or_404(Post, slug=slug)
    editable = request.user.is_authenticated() and request.user.is_staff
    if post.state == Post.HIDDEN and not editable:
        raise Http404
    comments = list(post.comments.all().order_by('date'))
    if (request.method == 'POST'):
        do_comment(request, post, request.POST, all_comments=comments)
        post = get_object_or_404(Post, slug=slug)
    comment_count = len([comment for comment in comments if not comment.spam])
    return render(request, 'post.html', { 'post': post,
                                          'editable':editable,
                                          'title':post.title,
                                          'mathjax':True,
                                          'comments':comments,
                                          'comment_count':comment_count})

def isLegitEmail(email):
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
    if all_comments is None:
        all_comments = list(post.comments.all())
    comment = Comment()
    comment.post = post
    comment.name = attrs['name'].strip()
    if len(comment.name) == 0:
        comment.name = 'Anonymous'
    comment.text = attrs['text']
    comment.email = attrs['email']
    comment.spam = akismet_check(request, comment)
    if isLegitEmail(comment.email):
        comment.subscribed = attrs.get('subscribed', False)
    else:
        comment.subscribed = False
        # make sure same ip has consistent gravatar
        comment.email = hashlib.sha1(comment.text.encode('utf-8')).hexdigest()
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

def utf8dict(d):
    out = {}
    for k, v in d.iteritems:
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Must be encoded in UTF-8; raise exception otherwise
            v.decode('utf8')
        out[k] = v
    return out

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
    r = urllib2.urlopen(url, data=urllib.urlencode(utf8dict(params))).read()
    if 'true' == r:
        return True
    else:
        return False

def tag(request, slug=None, page=None, title=None):
    postList = Post.objects.prefetch_related('tags').filter(state=Post.PUBLISHED).order_by('-datePosted')
    if page is None:
        page = 1
    else:
        page = int(page)
    if slug is None:
        page_root = '/archive'
    else:
        page_root = '/tag/' + slug
        tag = get_object_or_404(Tag, slug=slug)
        title = 'posts tagged ' + tag.name
        postList = postList.filter(tags__slug=slug)
    paginator = Paginator(postList, 4)
    if page > paginator.num_pages:
        raise Http404
    posts = paginator.page(page)
    if len(posts) == 0:
        raise Http404
    return render(request, 'tag.html', { 'posts':posts,
                                         'title':title,
                                         'page_root':page_root })

def archive(request, page=None):
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
        return md.unsafe_parser.reset().convert(post.excerpt)

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
