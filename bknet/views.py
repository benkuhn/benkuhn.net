from django.shortcuts import render_to_response
from posts.models import Post, Tag

def home(request):
    posts = Post.objects.filter(published=True).order_by('-datePosted')[:5]
    return render_to_response('home.html', { 'posts':posts, 'title':'Ben Kuhn' })

def contact(request):
    return render_to_response('contact.html', { 'title':'contact' })

def projects(request):
    return render_to_response('projects.html', { 'title': 'projects' })

def other(request):
    return render_to_response('other.html', { 'title':'other' })
