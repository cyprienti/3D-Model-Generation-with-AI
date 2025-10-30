import requests
import time
from models import PostModelsFromPromptRequest

API_BASE = "https://test-api.generio.ai"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJraGFsaWQuc2FsYW1hQHN0dWQudW5pLWR1ZS5kZSIsInBlcm1pc3Npb24iOlsic2tldGNoIiwibGlicmFyeSIsInNrZXRjaDIiXSwic3Vic2NyaXB0aW9uIjpudWxsLCJncm91cCI6bnVsbCwiZGV2ZWxvcGVyIjpmYWxzZSwiZXhwIjoxNzg0MTQ4MzkwLCJpYXQiOjE3NTI2MTIzOTAsInR5cGUiOiJhY2Nlc3MifQ.05XG-0wZTDDZr-Z9u9VqVk_-_QMOWjcAU7x3URZWADU"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def create_3d_model_from_prompt(prompt: str) -> str:
    url = f"{API_BASE}/models/from-prompt"
    payload = PostModelsFromPromptRequest(prompt_positive=prompt)
    response = requests.post(url, json=payload.model_dump(), headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        return data["assets"][0]["id"]
    else:
        raise Exception(f"Prompt-to-model failed: {response.status_code} - {response.text}")


def create_3d_model_from_asset(asset_id: str) -> str:
    url = f"{API_BASE}/models/from-assets"
    payload = {
        "assets": [
            {
                "id": asset_id,
                "file_key": "default"
            }
        ]
    }
    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        return data["assets"][0]["id"]
    else:
        raise Exception(f"Asset-to-model failed: {response.status_code} - {response.text}")


def get_model_base64(asset_id: str) -> str:
    url = f"{API_BASE}/assets/{asset_id}/files/default"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json()["files"]["default"]["data"]
    else:
        raise Exception(f"Model fetch failed: {response.status_code} - {response.text}")


def get_3d_model_from_text(prompt: str) -> str:
    asset_id = create_3d_model_from_prompt(prompt)
    time.sleep(10)
    return get_model_base64(asset_id)


def post_asset(base64_asset: str) -> str:
    url = f"{API_BASE}/assets"
    payload = {
        "file_data": base64_asset
    }

    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 200:
        return response.json()["assets"][0]["id"]
    else:
        raise Exception(f"Asset upload failed: {response.status_code} - {response.text}")


def get_3d_model_from_png(png_base64: str) -> str:
    asset_id = post_asset(png_base64)
    created_asset_id = create_3d_model_from_asset(asset_id)
    time.sleep(45)
    return get_model_base64(created_asset_id)




