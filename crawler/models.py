from django.db import models

class News(models.Model):
    title = models.CharField(max_length=100)
    time = models.CharField(max_length=30)
    summary = models.CharField(max_length=1000)
    content = models.CharField(max_length=10000)
    def __str__(self):
        return self.title

class Entry(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    key = models.CharField(max_length=20)
    def __str__(self):
        return self.key

class ContentEntry(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    key = models.CharField(max_length=20)
    def __str__(self):
        return self.key

# Create your models here.
