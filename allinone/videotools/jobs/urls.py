from django.urls import path
from .views import CreateJob, GetJob, GetFormats, get_progress

urlpatterns = [
    path('jobs/create/', CreateJob.as_view(), name='create-job'),
    path('jobs/<int:id>/', GetJob.as_view(), name='get-job'),
    path('jobs/get_formats/',GetFormats.as_view(), name='get-formats'),
    path('jobs/progress/<int:job_id>/',get_progress,name='get-progress'),
]