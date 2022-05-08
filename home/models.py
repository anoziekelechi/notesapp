from django.db import models
from django.conf import settings
# Create your models here.
from django.utils.text import slugify


class Note(models.Model):
    heading=models.CharField(max_length=100,unique=True)
    body=models.TextField()
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    slug=models.SlugField(null=True,max_length=100)

    class Meta:
        ordering=['created']

    def save(self, *args, **kwargs):  # (self,force_insert=False,force_update=False)
        self.slug = slugify(self.heading)

        return super(Note, self).save(*args, **kwargs)

    def __str__(self):
        return self.heading

'''
def save(self, *args, **kwargs): # new
      if not self.slug:
         self.slug = slugify(self.title)
      return super().save(*args, **kwargs)
'''