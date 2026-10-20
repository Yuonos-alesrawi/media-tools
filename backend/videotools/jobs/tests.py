"""Tests for the jobs app. Place this file at videotools/jobs/tests.py

Run:  python manage.py test
      (or in Docker: docker-compose exec web python manage.py test)

No Redis, Celery worker or internet is needed: the Celery task and the
download/format services are replaced with mocks.
"""
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from jobs.models import Jobs
from jobs.repositories.job_repository import JobRepository
from jobs.services.job_service import JobService


class JobsModelTests(TestCase):
    def test_website_name_is_filled_from_url(self):
        job = Jobs.objects.create(url="https://www.youtube.com/watch?v=abc", job_type="VID")
        self.assertEqual(job.website_name, "www.youtube.com")

    def test_website_name_is_not_overwritten(self):
        job = Jobs.objects.create(
            url="https://example.com/video", job_type="VID", website_name="custom"
        )
        self.assertEqual(job.website_name, "custom")

    def test_new_job_status_defaults_to_pending(self):
        job = Jobs.objects.create(url="https://example.com/v", job_type="Mp3")
        self.assertEqual(job.status, "pending")


class JobRepositoryTests(TestCase):
    def setUp(self):
        self.repo = JobRepository()

    def test_create_saves_url_type_and_format(self):
        job = self.repo.create("https://example.com/v", "VID", "22")
        saved = Jobs.objects.get(id=job.id)
        self.assertEqual(saved.url, "https://example.com/v")
        self.assertEqual(saved.job_type, "VID")
        self.assertEqual(saved.selected_format_id, "22")

    def test_mark_error_stores_status_and_message(self):
        job = self.repo.create("https://example.com/v", "VID")
        self.repo.mark_error(job, "network down")
        job.refresh_from_db()
        self.assertEqual(job.status, "error")
        self.assertEqual(job.error_message, "network down")


class JobServiceTests(TestCase):
    def setUp(self):
        self.download = MagicMock()
        self.service = JobService(
            repository=JobRepository(),
            download_service=self.download,
            format_service=MagicMock(),
        )

    def test_process_marks_job_done_on_success(self):
        job = self.service.create_job("https://example.com/v", "VID", "22")

        self.service.process(job.id)

        job.refresh_from_db()
        self.assertEqual(job.status, "done")
        self.download.download.assert_called_once()
        self.assertEqual(self.download.download.call_args.kwargs["format_id"], "22")

    def test_process_marks_job_error_when_download_fails(self):
        self.download.download.side_effect = RuntimeError("boom")
        job = self.service.create_job("https://example.com/v", "VID")

        self.service.process(job.id)

        job.refresh_from_db()
        self.assertEqual(job.status, "error")
        self.assertEqual(job.error_message, "boom")


class JobsApiTests(APITestCase):
    @patch("jobs.views.process_job")
    def test_create_job_returns_id_and_queues_task(self, mock_task):
        response = self.client.post(
            reverse("create-job"),
            {"url": "https://example.com/v", "type": "VID"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        job_id = response.data["id"]
        self.assertTrue(Jobs.objects.filter(id=job_id).exists())
        mock_task.delay.assert_called_once_with(job_id)

    @patch("jobs.views.process_job")
    def test_create_job_requires_url_and_type(self, mock_task):
        response = self.client.post(reverse("create-job"), {"url": ""}, format="json")

        self.assertEqual(response.status_code, 400)
        mock_task.delay.assert_not_called()
        self.assertEqual(Jobs.objects.count(), 0)

    def test_get_job_returns_its_data(self):
        job = Jobs.objects.create(url="https://example.com/v", job_type="VID")

        response = self.client.get(reverse("get-job", args=[job.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], job.id)
        self.assertEqual(response.data["status"], "pending")

    def test_get_job_returns_404_for_unknown_id(self):
        response = self.client.get(reverse("get-job", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_get_formats_requires_url(self):
        response = self.client.post(reverse("get-formats"), {}, format="json")
        self.assertEqual(response.status_code, 400)

    @patch("jobs.views.JobService.get_formats")
    def test_get_formats_returns_service_result(self, mock_get_formats):
        mock_get_formats.return_value = {
            "url": "https://example.com/v",
            "formats": [{"format_id": "22"}],
        }

        response = self.client.post(
            reverse("get-formats"), {"url": "https://example.com/v"}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["formats"], [{"format_id": "22"}])