from django.shortcuts import render
from posts.models import Post, Tag
from posts.views import tag

def home(request):
    return tag(request, title='Ben Kuhn')

def contact(request):
    return render(request, 'contact.html', { 'title':'contact' })

def projects(request):
    return render(request, 'projects.html', { 'title': 'projects' })

def privacy(request):
    return render(request, 'privacy.html', { 'title': 'privacy' })

def about(request):
    return render(request, 'about.html', { 'title': 'about' })

def bestof(request):
    return render(request, 'bestof.html', { 'title': 'best of' })

def keybase(request):
    return render(request, 'keybase.txt', content_type='text/plain')
