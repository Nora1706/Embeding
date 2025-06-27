import weaviate
from weaviate.classes.init import Auth
import os
nvidia_key = os.getenv("NVIDIA_APIKEY")
headers = {
    "X-NVIDIA-Api-Key": nvidia_key,
}


weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)

print(client.is_ready())  # Should print: `True`

client.close() 
