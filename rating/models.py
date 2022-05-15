from django.db import models

# Create your models here.
class Thumbnail(models.Model):
    img_url = models.URLField()
    title = models.TextField(max_length=100)
    yt_url = models.URLField(null=True)
    rating = models.IntegerField(default=1400)

class Round(models.Model):
    winner = models.ForeignKey(Thumbnail, models.CASCADE, related_name="winner")
    loser =  models.ForeignKey(Thumbnail, models.CASCADE, related_name="loser")
