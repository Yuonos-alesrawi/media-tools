from celery import shared_task

from .services.job_service import JobService


@shared_task
def process_job(job_id):
    JobService().process(job_id)


@shared_task
def test_celery():
    print("Celery is working!")
    return "OK"
