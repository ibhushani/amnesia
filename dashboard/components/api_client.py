"""
API Client for communicating with Amnesia FastAPI backend
"""
import requests
from typing import Dict, Any, Optional, List
from dashboard.config import API_BASE_URL, API_V1_PREFIX


class AmnesiaAPIClient:
    """Client for Amnesia API endpoints"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.api_url = f"{base_url}{API_V1_PREFIX}"
        self.session = requests.Session()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to API server"}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out"}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}
    
    # ═══════════════════════════════════════════════════════
    # Health & System
    # ═══════════════════════════════════════════════════════
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════════════════
    # Training
    # ═══════════════════════════════════════════════════════
    
    def start_training(
        self,
        model_type: str,
        num_shards: int = 4,
        epochs: int = 50,
        batch_size: int = 32,
    ) -> Dict[str, Any]:
        """Start a new training job"""
        return self._make_request(
            "POST",
            "/models/train",
            data={
                "model_type": model_type,
                "num_shards": num_shards,
                "epochs": epochs,
                "batch_size": batch_size,
            }
        )
    
    def get_training_status(self, job_id: str) -> Dict[str, Any]:
        """Get training job status"""
        return self._make_request("GET", f"/models/status/{job_id}")
    
    def list_models(self) -> Dict[str, Any]:
        """List all available models"""
        return self._make_request("GET", "/models")
    
    # ═══════════════════════════════════════════════════════
    # Unlearning
    # ═══════════════════════════════════════════════════════
    
    def start_unlearning(
        self,
        model_id: str,
        data_indices: List[int],
        alpha: float = 10.0,
        beta: float = 0.1,
        gamma: float = 0.01,
        epochs: int = 100,
    ) -> Dict[str, Any]:
        """Start an unlearning job"""
        return self._make_request(
            "POST",
            "/data/unlearn",
            data={
                "model_id": model_id,
                "data_indices": data_indices,
                "alpha": alpha,
                "beta": beta,
                "gamma": gamma,
                "epochs": epochs,
            }
        )
    
    def get_unlearning_status(self, job_id: str) -> Dict[str, Any]:
        """Get unlearning job status"""
        return self._make_request("GET", f"/data/status/{job_id}")
    
    # ═══════════════════════════════════════════════════════
    # Verification
    # ═══════════════════════════════════════════════════════
    
    def verify_erasure(
        self,
        shard_id: int,
        data_indices: List[int],
        threshold: float = 0.6,
    ) -> Dict[str, Any]:
        """Verify data erasure"""
        return self._make_request(
            "POST",
            "/verify/verify",
            data={
                "shard_id": shard_id,
                "data_indices": data_indices,
                "target_confidence_threshold": threshold,
            }
        )
    
    # ═══════════════════════════════════════════════════════
    # Certificates
    # ═══════════════════════════════════════════════════════
    
    def list_certificates(self) -> Dict[str, Any]:
        """List all certificates"""
        return self._make_request("GET", "/certificates")
    
    def download_certificate(self, cert_id: str) -> Optional[bytes]:
        """Download certificate PDF"""
        try:
            response = self.session.get(
                f"{self.api_url}/certificates/{cert_id}",
                timeout=30,
            )
            response.raise_for_status()
            return response.content
        except Exception:
            return None


# Singleton client instance
_client: Optional[AmnesiaAPIClient] = None


def get_api_client() -> AmnesiaAPIClient:
    """Get or create API client singleton"""
    global _client
    if _client is None:
        _client = AmnesiaAPIClient()
    return _client
