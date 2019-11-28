from django.db import models
from users.models import Businessman


class Video(models.Model):
    def get_upload_path(self, filename):
        return "{id}/video/{filename}".format(
               id = self.businessman.id,
               filename = filename,
               )

    businessman = models.ForeignKey(Businessman,on_delete=models.CASCADE) ##TODO
    title = models.CharField(max_length=255,blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    videofile = models.FileField(upload_to=get_upload_path, null=False, blank=False, max_length=254)

    def __str__(self):
        return "title:{},filename:{}".format(self.title,self.videofile)
