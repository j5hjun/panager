import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()

        # Log Request
        logger.info(f"Incoming Request: {request.method} {request.url}")

        try:
            response = await call_next(request)

            # Log Response
            process_time = time.time() - start_time
            logger.info(
                f"Request Completed: {request.method} {request.url} - "
                f"Status: {response.status_code} - Time: {process_time:.4f}s"
            )

            response.headers["X-Process-Time"] = str(process_time)
            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request Failed: {request.method} {request.url} - "
                f"Error: {e} - Time: {process_time:.4f}s"
            )
            raise e
