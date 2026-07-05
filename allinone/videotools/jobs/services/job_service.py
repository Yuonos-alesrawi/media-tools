from jobs.repositories.job_repository import JobRepository
from videodownloader.services.download_service import DownloadService
from videodownloader.services.format_service import FormatService


class JobService:
    def __init__(
        self,
        repository: JobRepository | None = None,
        download_service: DownloadService | None = None,
        format_service: FormatService | None = None,
    ):
        self.repository = repository or JobRepository()
        self.download_service = download_service or DownloadService()
        self.format_service = format_service or FormatService()

    def create_job(self, url: str, job_type: str, format_id: str | None = None):
        return self.repository.create(url, job_type, format_id)

    def get_job(self, job_id: int):
        return self.repository.get_by_id(job_id)

    def get_formats(self, url: str) -> dict:
        return self.format_service.get_formats(url)

    def process(self, job_id: int) -> None:
        job = self.repository.get_by_id(job_id)
        self.repository.mark_processing(job)
        try:
            self.download_service.download(job, format_id=job.selected_format_id)
            self.repository.mark_done(job)
        except Exception as e:
            self.repository.mark_error(job, str(e))
