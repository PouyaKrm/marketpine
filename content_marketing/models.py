from django.db import models
from users.models import Businessman,Customer


class Post(models.Model):
    def get_upload_path(self, filename):
        return "{id}/post/{filename}".format(
               id = self.businessman.id,
               filename = filename,
               )

    businessman = models.ForeignKey(Businessman,on_delete=models.CASCADE) ##TODO
    videofile = models.FileField(upload_to=get_upload_path, null=False, blank=False, max_length=254)
    title = models.CharField(max_length=255,blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return "id:{} , businessman:{}".format(self.id,self.businessman)

    def is_active(self):
        self.is_active = True
        self.save()


class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    body = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['creation_date']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.customer)



class Like(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='likes')
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'post',)
        ordering = ['creation_date']

    def __str__(self):
        return 'like by {}'.format(self.customer)
