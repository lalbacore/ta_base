
"""
Verify Crypto Simulation Endpoints

Tests the `simulate-break` API to ensure:
1. Invalidate Artifact -> signature_invalid
2. Invalidate Smart Contract -> unverified_registry
"""
import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://localhost:5002"

def get_json(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"❌ GET {url} failed: {e}")
        try:
             # Try to print the error body if available from e.read() within Exception?
             # e might be HTTPError which has read()
             if hasattr(e, 'read'):
                 print(f"Initial Error Content: {e.read().decode()}")
        except:
             pass
        return None

def post_json(url):
    try:
        req = urllib.request.Request(url, method="POST")
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"❌ POST {url} failed: {e}")
        return None

def main():
    print("🧪 Verifying Crypto Chain Simulation API...")

    # helper to find first completed workflow with artifacts
    missions = get_json(f"{BASE_URL}/api/mission/list")
    if not missions:
        sys.exit(1)

    workflow_id = None
    artifact_name = None

    for m in missions:
        if m.get('status') == 'completed':
             wid = m.get('workflow_id')
             artifacts = get_json(f"{BASE_URL}/api/workflow/{wid}/artifacts")
             if artifacts:
                 workflow_id = wid
                 artifact_name = artifacts[0]['name']
                 break
    
    if not workflow_id:
        print("⚠️ No completed workflow with artifacts found. Run e2e_mission_test.py first or ensure backend data exists.")
        sys.exit(0) # Not a failure of code, just missing data

    print(f"found workflow: {workflow_id}, artifact: {artifact_name}")

    # Test 0: Verify base trace works
    print("\n[Test 0] Get Artifact Chain")
    trace_data = get_json(f"{BASE_URL}/api/crypto-chain/artifact/{workflow_id}/{artifact_name}")
    if trace_data:
        print("✅ Success: Artifact chain retrieved")
    else:
        print("❌ Failed: Could not get artifact chain. Backend logic error.")
        sys.exit(1)

    # Test 1: Invalidate Artifact (signature_invalid)
    print("\n[Test 1] Invalidate Artifact (signature_invalid)")
    data = post_json(f"{BASE_URL}/api/crypto-chain/simulate-break/{workflow_id}/{artifact_name}/signature_invalid")
    if data:
        weak_links = [l['type'] for l in data.get('weak_links', [])]
        if 'invalid_signature' in weak_links:
             print("✅ Success: 'invalid_signature' weak link detected")
        else:
             print(f"❌ Failed: 'invalid_signature' not found in {weak_links}")
    else:
        print("❌ API Request Failed")

    # Test 2: Invalidate Smart Contract (unverified_registry)
    print("\n[Test 2] Invalidate Smart Contract (unverified_registry)")
    data = post_json(f"{BASE_URL}/api/crypto-chain/simulate-break/{workflow_id}/{artifact_name}/unverified_registry")
    if data:
        weak_links = [l['type'] for l in data.get('weak_links', [])]
        if 'unverified_registry' in weak_links:
             print("✅ Success: 'unverified_registry' weak link detected")
        else:
             print(f"❌ Failed: 'unverified_registry' not found in {weak_links}")
    else:
        print("❌ API Request Failed")

    print("\n✨ Verification Complete")

if __name__ == "__main__":
    main()
