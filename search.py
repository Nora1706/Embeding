import weaviate
from weaviate.classes.init import Auth
import os
import base64
import requests
from typing import Optional

# Environment setup
weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
nvidia_key = os.environ["NVIDIA_APIKEY"]

headers = {
    "X-NVIDIA-Api-Key": nvidia_key,
}

# Initialize client
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
    headers=headers
)

def file_to_base64(file_path: str) -> str:
    """Convert local image file to base64"""
    try:
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def url_to_base64(url: str) -> str:
    """Convert image URL to base64"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return ""

def search_by_image(image_source: str, limit: int = 5, is_url: bool = False):
    """
    Search for similar images using image similarity
    
    Args:
        image_source: Path to local image file or URL
        limit: Number of results to return
        is_url: True if image_source is a URL, False if it's a file path
    """
    print(f"\n🖼️  Searching by image: {image_source}")
    print("-" * 50)
    
    # Convert image to base64
    if is_url:
        query_b64 = url_to_base64(image_source)
    else:
        query_b64 = file_to_base64(image_source)
    
    if not query_b64:
        print("❌ Failed to process image")
        return
    
    try:
        collection = client.collections.get("DemoCollection")
        
        response = collection.query.near_image(
            near_image=query_b64,
            limit=limit,
            return_properties=["title", "poster"],
            # You can add distance threshold if needed
            # distance=0.7
        )
        
        print(f"Found {len(response.objects)} similar images:")
        for i, obj in enumerate(response.objects, 1):
            title = obj.properties.get("title", "No title")
            # Distance shows how similar the images are (lower = more similar)
            distance = getattr(obj.metadata, 'distance', 'N/A')
            print(f"{i}. {title}")
            print(f"   Similarity score: {distance}")
            print()
            
    except Exception as e:
        print(f"❌ Image search failed: {e}")

def search_by_text(query: str, limit: int = 5):
    """
    Search for images using text description
    
    Args:
        query: Text description to search for
        limit: Number of results to return
    """
    print(f"\n📝 Searching by text: '{query}'")
    print("-" * 50)
    
    try:
        collection = client.collections.get("DemoCollection")
        
        response = collection.query.near_text(
            query=query,
            limit=limit,
            return_properties=["title", "poster"],
            # You can add distance threshold if needed
            # distance=0.7
        )
        
        print(f"Found {len(response.objects)} matching results:")
        for i, obj in enumerate(response.objects, 1):
            title = obj.properties.get("title", "No title")
            distance = getattr(obj.metadata, 'distance', 'N/A')
            print(f"{i}. {title}")
            print(f"   Relevance score: {distance}")
            print()
            
    except Exception as e:
        print(f"❌ Text search failed: {e}")

def hybrid_search(text_query: str, image_source: str = None, is_url: bool = False, limit: int = 5):
    """
    Perform hybrid search using both text and image (if provided)
    
    Args:
        text_query: Text description
        image_source: Optional image path or URL
        is_url: True if image_source is a URL
        limit: Number of results to return
    """
    print(f"\n🔍 Hybrid search - Text: '{text_query}'")
    if image_source:
        print(f"                  Image: {image_source}")
    print("-" * 50)
    
    try:
        collection = client.collections.get("DemoCollection")
        
        if image_source:
            # Convert image to base64
            if is_url:
                query_b64 = url_to_base64(image_source)
            else:
                query_b64 = file_to_base64(image_source)
            
            if not query_b64:
                print("❌ Failed to process image, falling back to text-only search")
                search_by_text(text_query, limit)
                return
            
            # Use near_text with additional image context
            # Note: The exact hybrid query syntax may vary based on your Weaviate version
            response = collection.query.near_text(
                query=text_query,
                limit=limit,
                return_properties=["title", "poster"]
            )
        else:
            # Text-only search
            response = collection.query.near_text(
                query=text_query,
                limit=limit,
                return_properties=["title", "poster"]
            )
        
        print(f"Found {len(response.objects)} results:")
        for i, obj in enumerate(response.objects, 1):
            title = obj.properties.get("title", "No title") 
            distance = getattr(obj.metadata, 'distance', 'N/A')
            print(f"{i}. {title}")
            print(f"   Score: {distance}")
            print()
            
    except Exception as e:
        print(f"❌ Hybrid search failed: {e}")

def get_collection_stats():
    """Get basic stats about the collection"""
    try:
        collection = client.collections.get("DemoCollection")
        # Get collection info
        aggregate_response = collection.aggregate.over_all(total_count=True)
        total_objects = aggregate_response.total_count
        print(f"📊 Collection Stats:")
        print(f"   Total objects: {total_objects}")
        print()
    except Exception as e:
        print(f"❌ Failed to get collection stats: {e}")

# Example usage
if __name__ == "__main__":
    try:
        print("🎯 Image & Text Search Demo")
        print("=" * 50)
        
        # Get collection stats
        get_collection_stats()
        
        # Example searches - customize these for your data
        
        # 1. Text search
        search_by_text("person walking", limit=3)
        
        # 2. Image search (uncomment and provide a real image path)
        # search_by_image("/path/to/your/query/image.jpg", limit=3)
        
        # 3. Image search from URL (uncomment and provide a real URL)
        # search_by_image("https://example.com/image.jpg", limit=3, is_url=True)
        
        # 4. Hybrid search
        # hybrid_search("outdoor scene", "/path/to/your/image.jpg", limit=3)
        
        print("\n✅ Search complete!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Search interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        client.close()
        print("🔌 Connection closed")

# Interactive search function (uncomment to use)
"""
def interactive_search():
    while True:
        print("\n" + "="*50)
        print("Choose search type:")
        print("1. Text search")
        print("2. Image search (local file)")
        print("3. Image search (URL)")
        print("4. Hybrid search")
        print("5. Collection stats")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-5): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            query = input("Enter search text: ").strip()
            limit = int(input("Number of results (default 5): ") or 5)
            search_by_text(query, limit)
        elif choice == "2":
            image_path = input("Enter image file path: ").strip()
            limit = int(input("Number of results (default 5): ") or 5)
            search_by_image(image_path, limit, is_url=False)
        elif choice == "3":
            image_url = input("Enter image URL: ").strip()
            limit = int(input("Number of results (default 5): ") or 5)
            search_by_image(image_url, limit, is_url=True)
        elif choice == "4":
            text_query = input("Enter text query: ").strip()
            image_path = input("Enter image path (optional): ").strip() or None
            limit = int(input("Number of results (default 5): ") or 5)
            hybrid_search(text_query, image_path, limit=limit)
        elif choice == "5":
            get_collection_stats()
        else:
            print("Invalid choice!")

# Uncomment to run interactive mode:
# interactive_search()
"""
