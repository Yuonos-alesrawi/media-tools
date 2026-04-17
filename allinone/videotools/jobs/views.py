from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Jobs
from .serializer import JobSerializer
from .task import process_job
from videodownloader.chooseresolution import simplify_formats
from videodownloader.playlistinfo import get_playlist_details

# Create your views here.

class CreateJob(APIView):
    def post(self, request):
        url = request.data.get('url')
        job_type = request.data.get('type')
        format_id = request.data.get('format_id')

        if not url or not job_type:
            return Response({"error": "url and type are required"}, status=400)
        job = Jobs.objects.create(
            url = url,
            job_type = job_type,
            selected_format_id = format_id,
        )
        process_job.delay(job.id)
        return Response({'id':job.id})

class GetFormats(APIView):
    def post(self,request):
        url = request.data.get('url')
        if not url:
            return Response({"error": "url is required"}, status=400)
        if 'list=' in url:
            # نستخدم الدالة الجديدة للقوائم
            result = get_playlist_details(url)
            url = result.get("url")
            formats = result.get('formats')
        else:
            dict = simplify_formats(url)
            real_url = dict.get('url')
            formats = dict.get('formats')
            if real_url:
                url = real_url
        return Response({
                "url":url,
                "formats":formats
            })

class GetJob(APIView):
    def get(self, request, id):
        job = get_object_or_404(Jobs, id=id)
        serializer = JobSerializer(job)
        return Response(serializer.data)
