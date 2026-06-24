"""Helpers for handling multipart upload files and remote file inputs using httpx."""

import time

import httpx

from ...logger import LOG


async def iter_over_request_files(request, url_files):
    """Yield uploaded files and optional remote files as normalized tuples.

    Each yielded item is `(field_name, file_name, content_type, body_bytes)`.
    Files can come from multipart form uploads or from URLs listed in
    `url_files`.

    Args:
        request: FastAPI request object with files attribute
        url_files: List of URLs to download files from
    """
    # Handle multipart uploaded files
    if hasattr(request, "files") and request.files:
        for file_key, files in request.files.items():
            for f in files:
                file_name = getattr(f, "filename", "unknown")
                content_type = getattr(f, "content_type", "application/octet-stream")
                body = await f.read()
                LOG.info(f"File {file_name} from multipart has content type {content_type} and length bytes={len(body)}")
                yield file_key, file_name, content_type, body

    # Handle files from URL
    for file_key, list_url in {"url_files": url_files or []}.items():
        for url in sorted(set(list_url)):
            try:
                t_start = time.time()
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        body = resp.content
                        content_type = resp.headers.get("Content-Type", "UNKNOWN")
                    else:
                        raise RuntimeError(
                            "Failed to download file after %s seconds with code=%s from URL %s"
                            % (time.time() - t_start, resp.status_code, url)
                        )
            except Exception as e:
                raise e
            t_cost = time.time() - t_start
            LOG.info(f"File {url} has content type {content_type} and length bytes={len(body)}, downloaded in {t_cost} seconds")
            yield "url_files", url, content_type, body


def iter_over_request_files_sync(request, url_files):
    """Synchronous version of iter_over_request_files for backward compatibility.

    This is a sync wrapper that uses httpx sync client.
    """
    import httpx

    # Handle multipart uploaded files (from FastAPI form data)
    if hasattr(request, "_form"):
        form_data = request._form
        for file_key, files in form_data.multi_items():
            if isinstance(files, list):
                for f in files:
                    if hasattr(f, "read"):
                        body = f.read()
                        file_name = getattr(f, "filename", "unknown")
                        content_type = getattr(f, "content_type", "application/octet-stream")
                        LOG.info(
                            f"File {file_name} from multipart has content type {content_type} and length bytes={len(body)}"
                        )
                        yield file_key, file_name, content_type, body
            else:
                yield file_key, files, "text/plain", str(files).encode()

    # Handle files from URL
    for file_key, list_url in {"url_files": url_files or []}.items():
        for url in sorted(set(list_url)):
            try:
                t_start = time.time()
                with httpx.Client(follow_redirects=True) as client:
                    resp = client.get(url)
                    if resp.status_code == 200:
                        body = resp.content
                        content_type = resp.headers.get("Content-Type", "UNKNOWN")
                    else:
                        raise RuntimeError(
                            "Failed to download file after %s seconds with code=%s from URL %s"
                            % (time.time() - t_start, resp.status_code, url)
                        )
            except Exception as e:
                raise e
            t_cost = time.time() - t_start
            LOG.info(f"File {url} has content type {content_type} and length bytes={len(body)}, downloaded in {t_cost} seconds")
            yield "url_files", url, content_type, body
