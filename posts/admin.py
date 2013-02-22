from posts.models import Post, Tag
from django.contrib import admin

class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('title',)}

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
