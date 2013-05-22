from django.shortcuts import render
from posts.models import Post, Tag
from posts.views import tag

def home(request):
    return tag(request, title='Ben Kuhn')

def contact(request):
    return render(request, 'contact.html', { 'title':'contact' })

def projects(request):
    return render(request, 'projects.html', { 'title': 'projects' })
