from django.contrib import admin
from .models import Post,Comment,Like

class PostAdmin(admin.ModelAdmin):
    list_display = ('title','id','videofile','creation_date')

admin.site.register(Post,PostAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('post','customer','body')
    list_filter = ('creation_date',)
    search_fields = ('customer', 'body')
    # actions = ['approve_comments']

    # def approve_comments(self, request, queryset):
    #     queryset.update(active=True)

admin.site.register(Comment,CommentAdmin)

admin.site.register(Like)
