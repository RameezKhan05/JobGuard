from urllib.parse import quote
import httpx
from app.config import settings

class ControlMError(RuntimeError): pass

class ControlMClient:
    def __init__(self):
        self.base_url = settings.controlm_base_url.rstrip("/")
        self.token = settings.controlm_api_token
        self.timeout = settings.controlm_timeout_seconds
        self.verify = settings.controlm_ca_bundle or True

    def set_job_action(self, api_job_id: str, action: str) -> tuple[int, str]:
        if action not in {"HOLD", "RELEASE"}: raise ValueError("Unsupported action")
        if not self.token: raise ControlMError("CONTROLM_API_TOKEN is not configured")
        if "CHANGE_ME" in self.base_url: raise ControlMError("CONTROLM_BASE_URL is not configured")
        suffix = "hold" if action == "HOLD" else "free"
        # Job IDs contain a colon; encode it as a path segment for safe URL handling.
        job_id = quote(api_job_id, safe="")
        try:
            with httpx.Client(base_url=self.base_url, headers={"x-api-key": self.token, "Accept": "application/json"}, timeout=self.timeout, verify=self.verify) as client:
                response = client.post(f"/run/job/{job_id}/{suffix}")
        except httpx.TimeoutException as exc:
            raise ControlMError("TIMEOUT_UNKNOWN: reconcile current Control-M state before retrying") from exc
        except httpx.HTTPError as exc:
            raise ControlMError(f"Control-M transport error: {type(exc).__name__}") from exc
        if response.is_error:
            raise ControlMError(f"Control-M returned HTTP {response.status_code}")
        return response.status_code, "API accepted action; final state still needs verification"
