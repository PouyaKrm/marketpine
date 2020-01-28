from django.contrib import admin
from .models import Post,Comment,Like

class PostAdmin(admin.ModelAdmin):
    list_display = ('title','id','videofile','creation_date','businessman')
    list_filter = ('businessman',)
    search_fields = ('id', 'title')
admin.site.register(Post,PostAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('post','customer','body')
    list_filter = ('post','customer')
    search_fields = ('customer', 'body')
    # actions = ['approve_comments']

    # def approve_comments(self, request, queryset):
    #     queryset.update(active=True)

admin.site.register(Comment,CommentAdmin)

class LikeAdmin(admin.ModelAdmin):
    list_display = ('post','customer')
    list_filter = ('post','customer')
    # search_fields = ('customer', 'body')

admin.site.register(Like,LikeAdmin)
