import weaviate
import os
from weaviate.classes.init import Auth

# Make sure to include headers in your search script too
headers = {
    "X-NVIDIA-Api-Key": os.environ["NVIDIA_APIKEY"],
}

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.environ["WEAVIATE_URL"],
    auth_credentials=Auth.api_key(os.environ["WEAVIATE_API_KEY"]),
    headers=headers  # This is what's missing!
)

try:
    collection = client.collections.get("DemoCollection")
    response = collection.query.near_text(
        query="your search query here",
        limit=5
    )
    
    for item in response.objects:
        print(item.properties)
        
finally:
    client.close()  # This fixes the connection warning too
