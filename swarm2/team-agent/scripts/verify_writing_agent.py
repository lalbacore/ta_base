import requests
import json
import sys

BASE_URL = "http://localhost:5002/api"

def verify_agent_discovery():
    print("Verifying Writing Agent Discovery...")
    
    # 1. Discover all agents (filtering by type 'creative_writing' fails because type is 'specialist')
    response = requests.get(f"{BASE_URL}/mission/discover-agents")
    if response.status_code != 200:
        print(f"❌ Failed to discover agents: {response.text}")
        return False
        
    data = response.json()
    agents = data.get("agents", [])
    
    found = False
    for agent in agents:
        # Check by name OR by capability
        has_capability = any(c.get('capability_type') == 'creative_writing' for c in agent.get('capabilities', []))
        
        if agent["agent_name"] == "Writing Specialist" or has_capability:
            found = True
            print(f"✅ Found agent: {agent['agent_name']} (Type: {agent['agent_type']}, Trust: {agent['trust_score']})")
            if has_capability:
                print("   - Has 'creative_writing' capability")
            break
            
    if not found:
        print("❌ 'Writing Specialist' or agent with 'creative_writing' capability not found.")
        print(f"Agents found: {[a['name'] for a in agents]}")
        return False

    # 2. Match agents for a mission
    print("\nVerifying Mission Matching...")
    match_req = {
        "capability_type": "content_generation",
        "min_trust_score": 0
    }
    
    response = requests.post(f"{BASE_URL}/mission/match-agents", json=match_req)
    if response.status_code != 200:
        print(f"❌ Failed to match agents: {response.text}")
        return False
        
    data = response.json()
    matches = data.get("matches", [])
    
    if not matches:
        print("❌ No matches found for creative writing mission.")
        return False
        
    top_match = matches[0]
    print(f"Match keys: {top_match.keys()}")
    
    agent_data = top_match.get("agent", {})
    name = agent_data.get("agent_name") or agent_data.get("name")
    
    if name == "Writing Specialist":
        print(f"✅ Top match is correct: {name} (Score: {top_match.get('score')})")
    else:
        print(f"⚠️ Top match is {name}, expected 'Writing Specialist'")
        return False
        
    return True

if __name__ == "__main__":
    try:
        if verify_agent_discovery():
            print("\n✅ Verification Successful!")
            sys.exit(0)
        else:
            print("\n❌ Verification Failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running verification: {e}")
        sys.exit(1)
