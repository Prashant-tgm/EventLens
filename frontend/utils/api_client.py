import os
import requests
from typing import List, Dict, Any, Optional

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_V1 = f"{BACKEND_URL}/api/v1"

class APIClient:
    def __init__(self):
        self.token: Optional[str] = None
        self.headers: Dict[str, str] = {}

    def set_token(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}

    def clear_token(self):
        self.token = None
        self.headers = {}

    def login(self, email: str, password: str) -> bool:
        url = f"{API_V1}/auth/token"
        data = {"username": email, "password": password}
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.set_token(token_data["access_token"])
                return True
            return False
        except Exception as e:
            print(f"Login request error: {e}")
            return False

    def register(self, email: str, password: str, role: str = "photographer") -> Dict[str, Any]:
        url = f"{API_V1}/auth/register"
        data = {"email": email, "password": password, "role": role}
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def get_me(self) -> Dict[str, Any]:
        url = f"{API_V1}/auth/me"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    # Events API
    def create_event(self, name: str, date_str: str, event_type: str, location: str, description: str) -> Dict[str, Any]:
        url = f"{API_V1}/events/"
        data = {
            "name": name,
            "date": date_str,
            "event_type": event_type,
            "location": location,
            "description": description,
            "branding_config": {}
        }
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_events(self) -> List[Dict[str, Any]]:
        url = f"{API_V1}/events/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_event_details(self, event_id: str) -> Dict[str, Any]:
        url = f"{API_V1}/events/{event_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def invite_member(self, event_id: str, email: str, role: str = "photographer") -> Dict[str, Any]:
        url = f"{API_V1}/events/{event_id}/invite"
        data = {"email": email, "role": role}
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    # Photo Upload API (Direct S3 upload via Pre-signed URLs)
    def upload_photos_workflow(self, event_id: str, file_mappings: Dict[str, bytes]) -> str:
        """
        Orchestrates direct-to-S3 uploading in three parts:
        1. Request pre-signed URLs from backend.
        2. PUT file bytes directly to the storage URLs.
        3. Signal completion to trigger background AI worker.
        """
        filenames = list(file_mappings.keys())
        
        # 1. Initiate upload
        url = f"{API_V1}/photos/{event_id}/upload-initiate"
        res = requests.post(url, json={"filenames": filenames}, headers=self.headers)
        res.raise_for_status()
        initiate_data = res.json()
        
        upload_id = initiate_data["upload_id"]
        presigned_urls = initiate_data["urls"]
        
        # 2. Upload each file directly to storage URL
        for item in presigned_urls:
            filename = item["filename"]
            put_url = item["upload_url"]
            file_bytes = file_mappings[filename]
            
            # Perform direct PUT upload (does not pass through FastAPI server memory)
            headers = {"Content-Type": "image/jpeg"}
            put_res = requests.put(put_url, data=file_bytes, headers=headers)
            put_res.raise_for_status()
            
        # 3. Notify backend that upload is complete to start background job
        complete_url = f"{API_V1}/photos/{event_id}/upload-complete/{upload_id}"
        comp_res = requests.post(complete_url, headers=self.headers)
        comp_res.raise_for_status()
        
        return upload_id

    def check_upload_status(self, event_id: str, upload_id: str) -> Dict[str, Any]:
        url = f"{API_V1}/photos/{event_id}/upload-status/{upload_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    # Guest Selfie Search API
    def search_by_selfie(self, event_id: str, selfie_bytes: bytes) -> Dict[str, Any]:
        url = f"{API_V1}/search/{event_id}"
        files = {"file": ("selfie.jpg", selfie_bytes, "image/jpeg")}
        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()

    # Analytics API
    def get_owner_analytics(self) -> Dict[str, Any]:
        url = f"{API_V1}/analytics/owner"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_admin_analytics(self) -> Dict[str, Any]:
        url = f"{API_V1}/analytics/admin"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

api_client = APIClient()
