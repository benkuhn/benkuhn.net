from django.db import models

# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField()
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return '/tag/' + self.slug + '/1/'

class Post(models.Model):
    HIDDEN = 0
    PREVIEW = 1
    PUBLISHED = 2
    STATES = (
        (HIDDEN, 'Hidden'),
        (PREVIEW, 'Preview'),
        (PUBLISHED, 'Published'),
        )
    datePosted = models.DateTimeField(null=True)
    lastUpdated = models.DateTimeField(auto_now=True)
    state = models.IntegerField(choices=STATES)
    slug = models.SlugField()
    title = models.CharField(max_length=300)
    text = models.TextField(blank=True)
    excerpt = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, related_name="posts")
    def get_absolute_url(self):
        return '/' + self.slug
    def get_sendmail_url(self):
        return '/sendmail/' + self.slug
    def get_edit_url(self):
        return '/admin/posts/post/' + str(self.id) + '/'
    def __unicode__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments')
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    spam = models.BooleanField()
    subscribed = models.BooleanField()
    def get_absolute_url(self):
        return self.post.get_absolute_url() + '#comment-' + str(self.id)
    def __unicode__(self):
        ret = u'"%s" by %s' % (self.text[:30], self.email)
        if self.spam:
            ret += u' [SPAM]'
        return ret

class Subscription(models.Model):
    email = models.CharField(max_length=300)
