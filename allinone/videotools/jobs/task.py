from celery import shared_task
from videodownloader.videodownload import smart_download
from .models import Jobs


@shared_task
def process_job(job_id):
    job = Jobs.objects.get(id=job_id)
    job.status = "processing"
    job.save()
    try:
        smart_download(job, format_id=job.selected_format_id)
        job.status = "done"
    except Exception as e:
        job.status = "error"
        job.error_message = str(e)
    job.save()

@shared_task
def test_celery():
    print("Celery is working!")
    return "OK"
