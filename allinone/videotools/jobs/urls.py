from django.urls import path
from .views import CreateJob, GetJob, FormatsView

urlpatterns = [
    path('jobs/create/', CreateJob.as_view(), name='create-job'),
    path('jobs/<int:id>/', GetJob.as_view(), name='get-job'),
    path('jobs/get_formats/',FormatsView.as_view(), name='get-formats'),
]