from django.db import models

# Create your models here.

class Post(models.Model):
    datePosted = models.DateTimeField(null=True)
    lastUpdated = models.DateTimeField(auto_now=True)
    published = models.BooleanField()
    slug = models.SlugField()
    title = models.CharField(max_length=300)
    text = models.TextField()
    excerpt = models.TextField()
    def get_absolute_url(self):
        return '/posts/' + self.slug
    def __unicode__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField()
    posts = models.ManyToManyField(Post)
