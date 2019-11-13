from django.db import models



class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    videofile = models.FileField(upload_to='video/', null=True, blank=True)

    def __str__(self):
        return "title:{},filename:{}".format(self.title,self.videofile)
