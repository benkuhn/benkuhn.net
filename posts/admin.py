from posts.models import Post, Tag, Comment
from django.contrib import admin

class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('title',)}
    filter_horizontal = ('tags',)

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

class CommentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Comment, CommentAdmin)
