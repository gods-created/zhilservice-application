from django.db import models

class News(models.Model):
    title = models.CharField(max_length=200, name='title', unique=True)
    description = models.TextField(name='description')
    image_source = models.URLField(name='image_source')
    created_at = models.DateTimeField(name='created_at', auto_now_add=True)

    def to_json(self):
        return {
            'title': self.title,
            'description': self.description,
            'image_source': self.image_source,
            'created_at': self.created_at
        }
    
class Purchases(models.Model):
    short_description = models.TextField(name='short_description')
    file_source = models.URLField(name='file_source')
    created_at = models.DateTimeField(name='created_at', auto_now_add=True)

    def to_json(self):
        return {
            'short_description': self.short_description,
            'file_source': self.file_source,
            'created_at': self.created_at
        }