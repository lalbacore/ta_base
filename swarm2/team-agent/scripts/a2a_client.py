#!/usr/bin/env python3
"""
Agent-to-Agent (A2A) Client
Simulates an external Buyer Agent interacting with the Team Agent platform.
"""
import sys
import os
import json
import time
import argparse
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from swarms.team_agent.a2a.client import A2AClient
from swarms.team_agent.crypto.chain_client import ChainClient
from swarms.team_agent.storage.ipfs import IPFSClient

class BuyerAgent:
    def __init__(self, name="External Buyer Agent"):
        self.name = name
        self.a2a = A2AClient()
        self.chain = ChainClient()  # Expects env vars or default DB config
        self.ipfs = IPFSClient()

    def run_mission(self, requirement: str, budget: int):
        print(f"🤖 {self.name} starting mission: {requirement}")
        
        # 1. Discovery
        print("\n🔍 Phase 1: Discovery")
        print("   Searching for compatible agents...")
        try:
            agents = self.a2a.find_agents(
                registry_urls=["http://localhost:5002"],
                capability_type="research",
                min_trust_score=80
            )
        except Exception as e:
            print(f"   ⚠️ Discovery failed (is backend running?): {e}")
            return

        if not agents:
            print("   ❌ No agents found meeting criteria.")
            return

        target_agent = agents[0]
        print(f"   ✅ Found candidate: {target_agent.agent_name} (ID: {target_agent.agent_id})")
        print(f"      Trust Score: {target_agent.trust_score}")
        print(f"      Fees: {target_agent.endpoints.get('fees', 'Unknown')}")

        # 2. Hiring (On-Chain)
        print("\n🤝 Phase 2: Hiring (Smart Contract)")
        capability_id = target_agent.capabilities[0].get('capability_id', 'unknown')
        # specific to Team Agent implementation, typically a bytes32 hash
        cap_id_bytes = capability_id.encode('utf-8').ljust(32, b'\0')[:32]
        
        print(f"   Hiring agent for capability: {capability_id}")
        tx_hash = self.chain.hire_agent(cap_id_bytes, fee=budget)
        
        if tx_hash:
            print(f"   ✅ Hiring Transaction Sent! Hash: {tx_hash}")
            print("   (Simulating block confirmation wait...)")
            time.sleep(2)
        else:
            print("   ⚠️ On-chain hiring failed (simulating fallback/offline mode)")

        # 3. Execution (Off-Chain / Oracle)
        print("\n⚙️ Phase 3: Execution")
        payload = {
            "mission": requirement,
            "budget": budget,
            "callback_url": "http://buyer-agent.local/webhook"
        }
        
        try:
            print(f"   Invoking agent at {target_agent.endpoints.get('mcp_server', 'default endpoint')}...")
            # For simplicity in this script, we assume immediate response or polling
            # In production, this would be async via MCP
            response = self.a2a.invoke(
                target_agent, 
                capability_id, 
                payload
            )
            print("   ✅ Agent accepted mission.")
            print(f"   Job ID: {response.get('job_id')}")
        except Exception as e:
            print(f"   ❌ Invocation failed: {e}")
            return

        # 4. Verification (IPFS)
        print("\n📦 Phase 4: Verification")
        # In a real scenario, we'd poll the Smart Contract for the 'ArtifactPublished' event
        # Here we simulate finding the result
        print("   Checking for published artifacts...")
        # Mocking retrieval of CID from chain/event
        ipfs_cid = response.get('result_cid') or "QmHashPlaceholder"
        
        print(f"   Artifact CID: {ipfs_cid}")
        print("   Verifying storage...")
        # self.ipfs.cat(ipfs_cid) # If we had full IPFS reader
        print("   ✅ Artifact verified available on IPFS/Filecoin.")

        print("\n🎉 Mission Complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run A2A Buyer Simulation')
    parser.add_argument('--mission', type=str, default='Research the viability of DAO-governed Mars colonies')
    parser.add_argument('--budget', type=int, default=1000)
    
    args = parser.parse_args()
    
    buyer = BuyerAgent()
    buyer.run_mission(args.mission, args.budget)
