
import urllib.request
import json
import sys

def verify_metrics():
    print("🌍 Verifying Metrics API...")
    
    try:
        url = "http://localhost:5002/api/mission/stats"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
        print(f"✅ API Response Received: {json.dumps(data, indent=2)}")
        
        gov = data.get('governance', {})
        total = gov.get('total_decisions', 0)
        ai = gov.get('ai_approved', 0)
        human = gov.get('human_approved', 0)
        rejected = gov.get('rejected', 0)
        ratio = gov.get('autonomy_ratio', 0)
        
        print(f"📊 Stats: Total={total}, AI={ai}, Human={human}, Rejected={rejected}, Ratio={ratio:.2f}")
         
        # We expect at least 3 AI and 1 Human based on seed data
        # dec_001 (auto), dec_004 (auto), dec_005 (auto) -> 3 AI
        # dec_002 (human) -> 1 Human
        # dec_003 (rejected) -> 1 Rejected
        
        if ai >= 3 and human >= 1:
            print("✅ Metrics look correct (AI >= 3, Human >= 1)")
        else:
            print("⚠️  Metrics might be missing some seeded data")
            
    except Exception as e:
        print(f"❌ Failed to query API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_metrics()
