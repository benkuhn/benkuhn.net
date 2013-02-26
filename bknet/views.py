from django.shortcuts import render
from posts.models import Post, Tag

def home(request):
    posts = Post.objects.filter(published=True).order_by('-datePosted')[:5]
    return render(request, 'home.html', { 'posts':posts, 'title':'Ben Kuhn' })

def contact(request):
    return render(request, 'contact.html', { 'title':'contact' })

def projects(request):
    return render(request, 'projects.html', { 'title': 'projects' })

def other(request):
    return render(request, 'other.html', { 'title':'other' })
