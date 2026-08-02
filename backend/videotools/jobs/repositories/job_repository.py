from jobs.models import Jobs


class JobRepository:
    def get_by_id(self, job_id: int) -> Jobs:
        return Jobs.objects.get(id=job_id)

    def create(self, url: str, job_type: str, format_id: str | None = None) -> Jobs:
        return Jobs.objects.create(
            url=url,
            job_type=job_type,
            selected_format_id=format_id,
        )

    def mark_processing(self, job: Jobs) -> Jobs:
        job.status = "processing"
        job.save()
        return job

    def mark_done(self, job: Jobs) -> Jobs:
        job.status = "done"
        job.save()
        return job

    def mark_error(self, job: Jobs, message: str) -> Jobs:
        job.status = "error"
        job.error_message = message
        job.save()
        return job
