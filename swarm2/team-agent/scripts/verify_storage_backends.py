
import urllib.request
import json
import sys

def verify_backends():
    print("🌍 Verifying Storage Backends API...")
    
    try:
        url = "http://localhost:5002/api/storage/backends"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
        print(f"✅ API Response Received: {json.dumps(data, indent=2)}")
        
        # Check if local storage is present
        local_backend = next((b for b in data if b['storage_type'] == 'local'), None)
        
        if local_backend and local_backend['available']:
            print("✅ Local storage backend is available")
        else:
            print("❌ Local storage backend missing or unavailable")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Failed to query API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_backends()
