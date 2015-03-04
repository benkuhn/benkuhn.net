from django.shortcuts import render
from posts.models import Post, Tag
from posts.views import tag

def home(request):
    '''
    cat_names = ["tech", "effective-altruism", "misc"]
    cats = []
    for cat_name in cat_names:
        tag = Tag.objects.get(slug=cat_name)
        posts = tag.posts.filter(state=Post.PUBLISHED).order_by('-datePosted')[:5]
        cats.append({'tag':tag, 'posts':posts})
    '''
    posts = (Post.objects.prefetch_related('tags').filter(state=Post.PUBLISHED)
             .order_by('-datePosted')[:5])
    return render(request, 'home.html', {
        'title': 'Hi!',
        'posts': posts
        #'homepage_cats': cats
    })

def ea(request):
    return render(request, 'ea.html', { 'title':'altruism' })

def contact(request):
    return render(request, 'contact.html', { 'title':'contact' })

def projects(request):
    return render(request, 'projects.html', { 'title': 'projects' })

def privacy(request):
    return render(request, 'privacy.html', { 'title': 'privacy' })

def about(request):
    return render(request, 'about.html', { 'title': 'about' })

def more(request):
    return render(request, 'bestof.html', { 'title': 'read more' })

def keybase(request):
    return render(request, 'keybase.txt', content_type='text/plain')
