import weaviate
import weaviate.auth
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure, DataType, Multi2VecField, Property
import csv
import os
import base64
import time

# Environment variables
nvidia_key = os.environ["NVIDIA_APIKEY"]
weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
headers = {
    "X-NVIDIA-Api-Key": nvidia_key,
}
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
    headers=headers
)

# Convert image to base64
def url_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Load CSV annotations
image_dir = "/home/cirmlab/abc/weaviate-env/flickr-images/flickr30k_images/flickr30k_images"
csv_path = "/home/cirmlab/abc/weaviate-env/flickr-images/flickr30k_images/results.csv"
source_objects = []

with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter='|')
    reader.fieldnames = [f.strip() for f in reader.fieldnames]
    for row in reader:
        image_file = row["image_name"].strip()
        caption = (row.get("comment") or "").strip()
        full_path = os.path.join(image_dir, image_file)
        source_objects.append({
            "title": caption,
            "poster_path": full_path
        })

# Connect to Weaviate with NVIDIA API Key


# Upload in batch


collection = client.collections.get("DemoCollection")

with collection.batch.fixed_size(batch_size=200) as batch:
    for src_obj in source_objects:
        poster_b64 = url_to_base64(src_obj["poster_path"])
        weaviate_obj = {
            "title": src_obj["title"],
            "poster": poster_b64  # Add the image in base64 encoding
        }

        # The model provider integration will automatically vectorize the object
        batch.add_object(
            properties=weaviate_obj,
            
            # vector=vector  # Optionally provide a pre-obtained vector
        )
        time.sleep(3)
client.close()        
