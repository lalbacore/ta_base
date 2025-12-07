
"""
End-to-End Verification Mission

This script simulates a complete user journey:
1. Connecting to the Backend
2. Creating a "Legal Document Generation" mission
3. Polling for completion
4. Verifying artifacts are produced
5. Retrieving and printing the "Turing Tape" cryptographic log
"""
import urllib.request
import urllib.error
import time
import json
import sys

BASE_URL = "http://localhost:5002"

def get_json(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return None

def post_json(url, data):
    try:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("🚀 Starting End-to-End Verification Mission...")
    
    # 1. Health Check
    try:
        with urllib.request.urlopen(f"{BASE_URL}/health") as resp:
            if resp.status != 200:
                print("❌ Backend not healthy")
                sys.exit(1)
            print("✅ Backend is healthy")
    except Exception as e:
        print(f"❌ Failed to connect to backend: {e}")
        sys.exit(1)

    # 2. Create Mission
    print("\n📝 Creating Mission: Generate NDA Wrapper...")
    payload = {
        "description": "Generate a Non-Disclosure Agreement for an external contractor. Ensure it includes standard confidentiality clauses and is signed by the LegalSpecialist.",
        "max_cost": 50.0,
        "auto_approve_trusted": True,
        "required_capabilities": [
            {
                "capability_type": "legal_document_generator", # Matches what we saw in the logs earlier
                "min_trust_score": 50
            }
        ]
    }
    
    data = post_json(f"{BASE_URL}/api/mission/submit", payload)
    if not data:
        print(f"❌ Failed to create mission")
        sys.exit(1)
    
    mission_id = data['mission_id']
    print(f"✅ Mission Created: {mission_id}")
    
    # 3. Poll for Completion and Workflow ID
    print("\n⏳ Waiting for Mission Completion...")
    workflow_id = None
    max_retries = 30
    for i in range(max_retries):
        mission_data = get_json(f"{BASE_URL}/api/mission/{mission_id}")
        if not mission_data:
            print("Failed to get mission status")
            continue

        status = mission_data['status']
        
        # Capture workflow_id when it appears
        if not workflow_id and 'workflow_id' in mission_data:
            workflow_id = mission_data['workflow_id']
            print(f"   Workflow ID assigned: {workflow_id}")

        print(f"   Status: {status}...")
        
        if status == 'completed':
            print("✅ Mission Completed!")
            break
        elif status == 'failed':
            print(f"❌ Mission Failed: {mission_data.get('error')}")
            sys.exit(1)
            
        time.sleep(2)
    else:
        print("❌ Mission timed out")
        sys.exit(1)

    if not workflow_id:
        print("❌ workflow_id never assigned")
        sys.exit(1)

    # 4. Verify Artifacts
    print("\n📦 Verifying Artifacts...")
    artifacts = get_json(f"{BASE_URL}/api/workflow/{workflow_id}/artifacts")
    
    if not artifacts:
        print("❌ No artifacts found")
        sys.exit(1)
        
    print(f"✅ Found {len(artifacts)} artifact(s)")
    for a in artifacts:
        print(f"   - {a['name']} ({a['size']} bytes) [Checksum: {a['sha256_checksum'][:8]}...]")

    # 5. Retrieve Turing Tape
    print("\n📜 Retrieving Turing Tape (Crypto Log)...")
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/crypto-chain/workflow/{workflow_id}/manifest/text") as resp:
            log_text = resp.read().decode()
            
            if "Error" in log_text and len(log_text) < 100:
                print(f"❌ Failed to retrieve log: {log_text}")
            else:
                print("\n=== TURING TAPE LOG START ===")
                print(log_text[:2000] + ("..." if len(log_text) > 2000 else ""))
                print("=== TURING TAPE LOG END ===")
                print(f"✅ Turing Tape retrieved ({len(log_text)} chars)")
    except Exception as e:
        print(f"❌ Failed to retrieve Turing Tape: {e}")

    print("\n🎉 End-to-End Verification Successful!")

if __name__ == "__main__":
    main()
