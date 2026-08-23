"""Background task definitions."""

from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.check_broken_links")
def check_broken_links() -> dict[str, int]:
    return {"checked": 0, "broken": 0}


@celery_app.task(name="app.workers.tasks.purge_temp_documents")
def purge_temp_documents() -> dict[str, int]:
    return {"purged": 0}


@celery_app.task(name="app.workers.tasks.run_crawl")
def run_crawl(source_id: str) -> dict[str, str]:
    return {"source_id": source_id, "status": "queued"}


@celery_app.task(name="app.workers.tasks.batch_embed")
def batch_embed(document_ids: list[str] | None = None) -> dict[str, int]:
    return {"embedded": len(document_ids or [])}
