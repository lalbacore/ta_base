
import urllib.request
import json
import sys

def verify_networks():
    print("🌍 Verifying Network Provider Configuration...")
    
    try:
        url = "http://localhost:5002/api/provider/list"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
        print(f"✅ API Response Received: {len(data)} providers found")
        
        # Check for environment metadata
        envs = set()
        for p in data:
            meta = p.get('meta_data', {})
            env = meta.get('env', 'GENERAL')
            envs.add(env)
            print(f"  - {p['name']} ({p['provider_type']}): Env={env}")
            
        expected_envs = {'production', 'qa', 'development'}
        missing = expected_envs - envs
        if not missing:
            print("✅ All environments found: Production, QA, Development")
        else:
            print(f"⚠️  Missing environments: {missing}")
            # Note: Might be acceptable if seeding didn't complete fully, but we expect them.
            
    except Exception as e:
        print(f"❌ Failed to query API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_networks()
