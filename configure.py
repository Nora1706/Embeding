import weaviate
from weaviate.classes.init import Auth
import os
from weaviate.classes.config import Configure, DataType, Multi2VecField, Property
weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
nvidia_key = os.environ["NVIDIA_APIKEY"]

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)

client.collections.create(
    "DemoCollection",
    properties=[
        Property(name="title", data_type=DataType.TEXT),
        Property(name="poster", data_type=DataType.BLOB),
    ],
    vectorizer_config=[
        Configure.NamedVectors.multi2vec_nvidia(
            name="title_vector",
            # Define the fields to be used for the vectorization - using image_fields, text_fields
            image_fields=[
                Multi2VecField(name="poster", weight=0.9)
            ],
            text_fields=[
                Multi2VecField(name="title", weight=0.1)
            ],
        )
    ],
    # Additional parameters not shown
)
client.close()
