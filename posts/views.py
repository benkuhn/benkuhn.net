from django.shortcuts import render, get_object_or_404
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponseRedirect
from models import Post, Tag, Comment, Subscription
from django.db.models import Q
import md5, urllib, urllib2, hashlib
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMessage
import md

# /<slug>
# view for a single post, e.g. http://benkuhn.net/www-prefix
def by_slug(request, slug=''):
    post = get_object_or_404(Post, slug=slug)
    # should we insert an "edit" link?
    editable = request.user.is_authenticated() and request.user.is_staff
    if post.state == Post.HIDDEN and not editable:
        raise Http404
    comments = list(post.comments.all().order_by('date'))
    if (request.method == 'POST'):
        # we're being commented on
        do_comment(request, post, request.POST, all_comments=comments)
        return HttpResponseRedirect(post.get_absolute_url())
    comment_count = len([comment for comment in comments if not comment.spam])
    return render(request, 'post.html', { 'post': post,
                                          'editable':editable,
                                          'title':post.title,
                                          'mathjax':True,
                                          'comments':comments,
                                          'comment_count':comment_count})

# /sendmail/<slug>
# send updates for a newly-published post
def send_emails(request, slug=''):
    post = get_object_or_404(Post, slug=slug)
    # make sure only I can send email
    editable = request.user.is_authenticated() and request.user.is_staff
    if post.state == Post.HIDDEN or not editable:
        raise Http404
    subs = Subscription.objects.all()
    # de-duplicate emails by putting them in a set
    emails = list(set([sub.email for sub in subs]))
    template = get_template('post_email.html')
    subject = "New post at benkuhn.net: \"%s\"" % post.title
    for email in emails:
        text = template.render(Context({
                    'post':post,
                    'email':email }))
        msg = EmailMessage(subject, text, "robot@benkuhn.net", [email])
        msg.content_subtype = 'html'
        msg.send()
    return render(request, 'sent.html', { 'title':'Sent!' })

# /preview/
# preview a Markdown thing
def preview(request):
    text = request.POST.get('text', '')
    return render(request, 'preview.html', { 'text':text })

def isLegitEmail(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

# all the processing associated with a posted comment: spam filtering,
# sending emails to subscribers, etc.
#
# 'attrs' is the form data to use;
# 'all_comments' can optionally be supplied if it's been prefetched,
# and otherwise is list(post.comments.all()).
def do_comment(request, post, attrs, all_comments=None):
    # make sure the form came through correctly
    if not ('name' in attrs
            and 'text' in attrs
            and 'email' in attrs
            and 'lastname' in attrs):
        return False
    # 'lastname' is a honeypot field
    if not attrs['lastname'] == "":
        return False
    # keyword parameter is for prefetching
    if all_comments is None:
        all_comments = list(post.comments.all())
    ### create a new comment record
    comment = Comment()
    comment.post = post
    comment.name = attrs['name'].strip()
    if len(comment.name) == 0:
        comment.name = 'Anonymous'
    comment.text = attrs['text']
    comment.email = attrs['email']
    ### check for spam (requires a web request to Akismet)
    comment.spam = akismet_check(request, comment)
    if isLegitEmail(comment.email):
        comment.subscribed = attrs.get('subscribed', False)
    else:
        comment.subscribed = False
        # make sure comments under the same name have a consistent gravatar
        comment.email = hashlib.sha1(comment.name.encode('utf-8')).hexdigest()
    comment.save()
    all_comments.append(comment)
    if comment.spam:
        return # don't email people for spam comments!
    ### send out notification emails
    emails = {}
    for c in all_comments:
        if c.subscribed and c.email != comment.email and isLegitEmail(c.email):
            emails[c.email] = c.name
    for name, email in settings.MANAGERS:
        emails[email] = name
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

# /unsub/<slug>/<email>
# handle unsubscribe links from emails
def unsub(request, slug='', email=''):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(email=email).update(subscribed=False)
    return render(request, 'unsub.html', { 'title':'farewell' })

# /email/
# display the "subscribe via email" form and handle submissions
def email(request):
    if request.method == 'POST':
        email = request.POST['email']
        if isLegitEmail(email) and request.POST['lastname'] == '':
            o = Subscription(email=email)
            o.save()
            template = get_template('subscribe_email.html')
            text = template.render(Context({
                        'email': email
                        }))
            print 'text!!!'
            msg = EmailMessage("Thanks for subscribing!", text, "robot@benkuhn.net", [email])
            msg.content_subtype = 'html'
            msg.send()
            emails = [e for (name, e) in settings.MANAGERS]
            msg2 = EmailMessage(email + " subscribed to benkuhn.net", "", "robot@benkuhn.net", emails)
            msg2.send()
        return render(request, 'sub.html', { 'title': 'thanks :)',
                                             'email': email })
    else:
        return render(request, 'email.html', { 'title': 'subscribe via email' })

# /subscribers/
# for me to get a list of my email subscribers
def subscribers(request):
    if not (request.user.is_authenticated() and request.user.is_staff):
        raise Http404
    subs = Subscription.objects.all()
    return render(request, 'subscribers.html', { 'title': 'subscribers',
                                                 'subscribers': subs })

# /unsub/<email>
# allow blog subscribers to unsubscribe
def global_unsub(request, email=''):
    o = get_object_or_404(Subscription, email=email)
    o.delete()
    return render(request, 'unsub.html', { 'title':'farewell' })

# convenience method for helping Akismet with stuff
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# helper method for Akismet encoding sadness
#
# public domain code from somewhere, likely Stack Overflow, but I
# don't remember where
def utf8dict(d):
    out = {}
    for k, v in d.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Must be encoded in UTF-8; raise exception otherwise
            v.decode('utf8')
        out[k] = v
    return out

# fill out the data Akismet needs
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

# /tag/<slug>/<page>/
# handles all posts for a certain tag e.g. benkuhn.net/rationality
#
# 'page' is for in case you want to show older posts
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
    paginator = Paginator(postList, 10)
    if page > paginator.num_pages:
        raise Http404
    if page < 1:
        raise Http404
    posts = paginator.page(page)
    if len(posts) == 0:
        raise Http404
    return render(request, 'tag.html', { 'posts':posts,
                                         'title':title,
                                         'page_root':page_root })

# /archive/<page>/
def archive(request, page=None):
    return tag(request, slug=None, page=page, title='archive')

# fills in the appropriate getters for an RSS feed
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
        return md.unsafe_parser.reset().convert(post.text)

    item_guid_is_permalink = False
    def item_guid(self, post):
        return md5.new(str(post.id)).hexdigest()

    def item_categories(self, post):
        return [tag.name for tag in post.tags.all()]

# /rss/
rss = RssFeed()

# /q/
# list all the unpublished posts for easy browsing
def queue(request):
    if not (request.user.is_authenticated() and request.user.is_staff):
        raise Http404
    posts = Post.objects.filter(~Q(state=Post.PUBLISHED))
    postsByLength = posts.extra(select={'length':'Length(text)'}).order_by('-length')
    return render(request, 'queue.html', { 'posts':postsByLength, 'title':'queue' })
