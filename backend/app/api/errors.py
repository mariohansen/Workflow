from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.errors import (
    DomainError,
    NoWorkflowVersionError,
    RunNotFoundError,
    WorkflowNotFoundError,
    WorkflowValidationError,
)
from app.engine.registry import UnknownStepTypeError

_STATUS_BY_ERROR: dict[type[DomainError], int] = {
    WorkflowNotFoundError: 404,
    WorkflowValidationError: 422,
    NoWorkflowVersionError: 422,
    RunNotFoundError: 404,
    UnknownStepTypeError: 422,
}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        details: object = None
        if isinstance(exc, WorkflowValidationError):
            details = [{"code": v.code, "message": v.message} for v in exc.violations]

        return JSONResponse(
            status_code=_STATUS_BY_ERROR.get(type(exc), 400),
            content={"code": exc.code, "message": str(exc), "details": details},
        )
