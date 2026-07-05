from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Jobs
from .serializer import JobSerializer
from .services.job_service import JobService
from .task import process_job


class CreateJob(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.job_service = JobService()

    def post(self, request):
        url = request.data.get("url")
        job_type = request.data.get("type")
        format_id = request.data.get("format_id")

        if not url or not job_type:
            return Response({"error": "url and type are required"}, status=400)

        job = self.job_service.create_job(url, job_type, format_id)
        process_job.delay(job.id)
        return Response({"id": job.id})


class FormatsView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.job_service = JobService()

    def post(self, request):
        url = request.data.get("url")
        if not url:
            return Response({"error": "url is required"}, status=400)

        result = self.job_service.get_formats(url)
        resolved_url = result.get("url") or url
        return Response({"url": resolved_url, "formats": result.get("formats")})


class GetJob(APIView):
    def get(self, request, id):
        job = get_object_or_404(Jobs, id=id)
        serializer = JobSerializer(job)
        return Response(serializer.data)
