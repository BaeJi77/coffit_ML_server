import json

import requests
from django.http import JsonResponse


def post_list(request):
    if request.method == "POST":
        body = json.loads(request.body)
        r = requests.get('https://api.coffitnow.com/trainers')
        # 추후 밑에 라인 고쳐서 put 요청하면 됨
        # 필요한 사항. exerciseVideoId + s3 동영상 위치 -> 파일 겟해야 됨
        # r = requests.put('https://api.coffitnow.com//exerciseVideos/tags/{exerciseVideoId}')
        print(r)
        print(body)
        return JsonResponse(body)