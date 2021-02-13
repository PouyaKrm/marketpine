from django.contrib import admin
from .models import Post, Comment, Like, ContentMarketingSettings, ViewedPost


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'videofile', 'create_date', 'businessman', 'confirmation_status')
    list_filter = ('businessman',)
    search_fields = ('id', 'title')


admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'customer', 'body')
    list_filter = ('post', 'customer')
    search_fields = ('customer', 'body')
    # actions = ['approve_comments']

    # def approve_comments(self, request, queryset):
    #     queryset.update(active=True)


admin.site.register(Comment,CommentAdmin)


class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'customer')
    list_filter = ('post','customer')


admin.site.register(Like, LikeAdmin)


class ContentSettingAdminModel(admin.ModelAdmin):

    list_display = ['businessman', 'message_template', 'send_video_upload_message']


admin.site.register(ContentMarketingSettings, ContentSettingAdminModel)


class ViewedPostAdminModel(admin.ModelAdmin):

    list_display = ['post', 'customer', 'create_date']


admin.site.register(ViewedPost, ViewedPostAdminModel)


