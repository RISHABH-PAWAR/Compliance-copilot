"""Global Error Handler"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.logging import get_logger

logger = get_logger("error_handler")


def register_error_handlers(app: FastAPI):
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(status_code=404, content={"detail": "Resource not found"})

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        import traceback
        from app.config import get_settings
        settings = get_settings()
        
        err_msg = str(exc)
        tb = traceback.format_exc()
        logger.error("internal_error", path=request.url.path, error=err_msg, traceback=tb)
        
        content = {"detail": "Internal server error"}
        if settings.APP_ENV == "development":
            content["error"] = err_msg
            content["traceback"] = tb
            
        return JSONResponse(status_code=500, content=content)

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc):
        import traceback
        from app.config import get_settings
        settings = get_settings()
        
        err_msg = str(exc)
        tb = traceback.format_exc()
        logger.error("unhandled_error", path=request.url.path, error=err_msg, type=type(exc).__name__, traceback=tb)
        
        content = {"detail": "An unexpected error occurred"}
        if settings.APP_ENV == "development":
            content["error"] = err_msg
            content["traceback"] = tb
            
        return JSONResponse(status_code=500, content=content)
