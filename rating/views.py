from django.http import HttpRequest, JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from .models import Thumbnail, Round
import random
import os
import base64
import requests

IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")

# Create your views here.
def index(request):
    if request.method == "POST":
        winner_id = int(request.POST["winner"])
        loser_id = int(request.POST["loser"])

        winner_thumb = Thumbnail.objects.get(id=winner_id)
        loser_thumb = Thumbnail.objects.get(id=loser_id)

        Rw, Rl = rating_calc(winner_thumb.rating, loser_thumb.rating)

        winner_thumb.rating = Rw
        winner_thumb.save()
        loser_thumb.rating = Rl
        loser_thumb.save()

        return redirect("/")

    else:
        thumbnails = list(Thumbnail.objects.filter())
        random.shuffle(thumbnails)

        thumb1, thumb2 = thumbnails[0], thumbnails[1]

        return render(request, "rating/index.html", {
            "thumb1": thumb1,
            "thumb2": thumb2
        })

def rankings(request):
    thumbnails = Thumbnail.objects.filter().order_by('-rating')
    return render(request, "rating/rank.html", {
        "thumbnails": thumbnails
    })

def upload_image(request):
    if request.method == "POST":
        return HttpResponse(imgur_upload(request.FILES['file'])["data"]["link"])
    else:
        return render(request, "rating/upload.html")

def imgur_upload(file):
    res = requests.post("https://api.imgur.com/3/image", headers={
        "Authorization": f"Client-ID {IMGUR_CLIENT_ID}"
    }, data={
        'image': file.file.read(),
        'url': 'file'
    }, files=[])

    return res.json()

def add_thumbnail(request):
    if request.method == "POST":
        if request.POST["option"] == "youtube":
            # https://i3.ytimg.com/vi/VIDEO-ID/maxresdefault.jpg
            youtube_url = request.POST["youtube_url"]
            video_id = youtube_url.split("?v=")[1]
            img_url = f"https://i3.ytimg.com/vi/{video_id}/maxresdefault.jpg"
            Thumbnail(img_url=img_url, title=get_yt_title(video_id), yt_url=youtube_url, rating=1400).save()
        else:
            Thumbnail(img_url=request.POST["img_url"], title=request.POST["title"], rating=1400).save()
        return redirect("/add")

    else:
        return render(request, "rating/add.html")

def get_yt_title(vid_id):
    import urllib.request
    import json
    import urllib

    #change to yours VideoID or change url inparams
    params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % vid_id}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        return data['title']

def rating_calc(winner_rating, loser_rating):
    """
    Follows Elo's Ranking System
    """
    K = 20
    Ewinner = 1/(1 + 10.0 ** ((loser_rating-winner_rating) / 400) )
    Eloser = 1/(1 + 10.0 ** ((winner_rating-loser_rating) / 400) )

    Rwinner = winner_rating + K * (1 - Ewinner)
    Rloser = loser_rating + K * (0 - Eloser)

    print(Rwinner, Rloser)

    return (Rwinner, Rloser)

def delete_thumbnail(request, thumb_id):
    Thumbnail.objects.get(id=thumb_id).delete()
    return redirect("/rank")
