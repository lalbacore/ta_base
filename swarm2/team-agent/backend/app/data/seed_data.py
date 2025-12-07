"""
Seed data for Team Agent Platform UI.
Provides realistic sample data for all components.
"""
from datetime import datetime, timedelta

# Helper to generate timestamps
def timestamp(days_ago=0, hours_ago=0, minutes_ago=0):
    dt = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
    return dt.isoformat()


# ============================================================================
# MISSIONS & WORKFLOWS
# ============================================================================

SAMPLE_MISSIONS = [
    {
        'mission_id': 'mission_001',
        'description': 'Publish Research Paper: "Agents in Decentralized Economies" to ArXiv',
        'required_capabilities': [
            {'capability_type': 'research', 'min_trust_score': 90, 'max_cost': 50},
            {'capability_type': 'scientific_writing', 'min_trust_score': 95, 'max_cost': 100},
            {'capability_type': 'citation_review', 'min_trust_score': 85, 'max_cost': 30}
        ],
        'min_trust_score': 85,
        'max_cost': 200,
        'breakpoints': ['draft_approval', 'final_review'],
        'auto_approve_trusted': True,
        'auto_approve_threshold': 95,
        'created_at': timestamp(days_ago=1)
    },
    {
        'mission_id': 'mission_002',
        'description': 'Create DAO Governance Proposal: "Funding Allocation for Q3 2025"',
        'required_capabilities': [
            {'capability_type': 'governance_design', 'min_trust_score': 95, 'max_cost': 80},
            {'capability_type': 'financial_analysis', 'min_trust_score': 90, 'max_cost': 60}
        ],
        'min_trust_score': 90,
        'max_cost': 150,
        'breakpoints': ['proposal_review'],
        'auto_approve_trusted': False,
        'auto_approve_threshold': 98,
        'created_at': timestamp(hours_ago=12)
    },
    {
        'mission_id': 'mission_003',
        'description': 'Smart Contract Audit: CapabilityMarketplace.sol Security Review',
        'required_capabilities': [
            {'capability_type': 'security_audit', 'min_trust_score': 98, 'max_cost': 200}
        ],
        'min_trust_score': 95,
        'max_cost': 250,
        'breakpoints': [],
        'auto_approve_trusted': True,
        'auto_approve_threshold': 95,
        'created_at': timestamp(hours_ago=4)
    },
    {
        'mission_id': 'mission_004',
        'description': 'Generate Tech Podcast: "Daily Decentralization Update"',
        'required_capabilities': [
            {'capability_type': 'content_generation', 'min_trust_score': 80, 'max_cost': 40},
            {'capability_type': 'audio_synthesis', 'min_trust_score': 85, 'max_cost': 60}
        ],
        'min_trust_score': 80,
        'max_cost': 120,
        'breakpoints': ['script_approval'],
        'auto_approve_trusted': True,
        'auto_approve_threshold': 90,
        'created_at': timestamp(minutes_ago=45)
    }
]

SAMPLE_WORKFLOWS = [
    {
        'workflow_id': 'wf_mission_001',
        'mission_id': 'mission_001',
        'status': 'completed',
        'progress': 100,
        'current_stage': 'recorder',
        'created_at': timestamp(days_ago=1),
        'updated_at': timestamp(days_ago=1, hours_ago=-1),
        'stages': [
            {
                'stage_name': 'initializing',
                'status': 'completed',
                'started_at': timestamp(days_ago=1),
                'completed_at': timestamp(days_ago=1, minutes_ago=-2),
                'output': {'message': 'Research workflow initialized'}
            },
            {
                'stage_name': 'architect',
                'status': 'completed',
                'started_at': timestamp(days_ago=1, minutes_ago=-2),
                'completed_at': timestamp(days_ago=1, minutes_ago=-30),
                'output': {'outline': 'Abstract, Introduction, Methodology, Results, Conclusion', 'citations': 24}
            },
            {
                'stage_name': 'builder',
                'status': 'completed',
                'started_at': timestamp(days_ago=1, minutes_ago=-30),
                'completed_at': timestamp(days_ago=1, minutes_ago=-90),
                'output': {'draft_generated': True, 'word_count': 4500}
            },
            {
                'stage_name': 'critic',
                'status': 'completed',
                'started_at': timestamp(days_ago=1, minutes_ago=-90),
                'completed_at': timestamp(days_ago=1, hours_ago=-2),
                'output': {'score': 0.94, 'feedback': 'Minor formatting issues in citations'}
            },
            {
                'stage_name': 'recorder',
                'status': 'completed',
                'started_at': timestamp(days_ago=1, hours_ago=-2),
                'completed_at': timestamp(days_ago=1, hours_ago=-1),
                'output': {'published_to_arxiv': True, 'doi': '10.48550/arXiv.2512.01234'}
            }
        ]
    }
]

# ============================================================================
# BREAKPOINTS
# ============================================================================

SAMPLE_BREAKPOINTS = [
    {
        'breakpoint_id': 'bp_001',
        'workflow_id': 'wf_mission_004',
        'breakpoint_type': 'script_approval',
        'status': 'pending',
        'created_at': timestamp(minutes_ago=10),
        'options': [
            {'option_id': 'opt_1', 'label': 'Approve Script A (More Technical)', 'score': 0.92},
            {'option_id': 'opt_2', 'label': 'Approve Script B (More Casual)', 'score': 0.88}
        ]
    }
]

# ============================================================================
# PKI CERTIFICATES
# ============================================================================

SAMPLE_CERTIFICATES = {
    'root': {
        'domain': 'root',
        'subject': 'CN=Team Agent Root CA',
        'issuer': 'CN=Team Agent Root CA',
        'serial_number': 'A1B2C3D4E5F6',
        'valid_from': timestamp(days_ago=365),
        'valid_to': timestamp(days_ago=-365),
        'status': 'valid',
        'key_size': 4096,
        'signature_algorithm': 'SHA256-RSA'
    },
    'government': {
        'domain': 'government',
        'subject': 'CN=Team Agent Government',
        'issuer': 'CN=Team Agent Root CA',
        'serial_number': 'B2C3D4E5F6A7',
        'valid_from': timestamp(days_ago=180),
        'valid_to': timestamp(days_ago=-185),
        'status': 'valid',
        'key_size': 2048,
        'signature_algorithm': 'SHA256-RSA'
    },
    'execution': {
        'domain': 'execution',
        'subject': 'CN=Team Agent Execution',
        'issuer': 'CN=Team Agent Root CA',
        'serial_number': 'C3D4E5F6A7B8',
        'valid_from': timestamp(days_ago=90),
        'valid_to': timestamp(days_ago=-275),
        'status': 'valid',
        'key_size': 2048,
        'signature_algorithm': 'SHA256-RSA'
    },
    'logging': {
        'domain': 'logging',
        'subject': 'CN=Team Agent Logging',
        'issuer': 'CN=Team Agent Root CA',
        'serial_number': 'D4E5F6A7B8C9',
        'valid_from': timestamp(days_ago=30),
        'valid_to': timestamp(days_ago=-335),
        'status': 'valid',
        'key_size': 2048,
        'signature_algorithm': 'SHA256-RSA'
    }
}

REVOKED_CERTIFICATES = []

# ============================================================================
# TRUST SCORES & AGENTS
# ============================================================================

SAMPLE_AGENTS = [
    {
        'agent_id': 'agent_research_001',
        'name': 'DeepScience AI',
        'type': 'research',
        'trust_score': 96,
        'reputation': 4.9,
        'total_operations': 85,
        'success_rate': 0.98,
        'security_incidents': 0,
        'policy_violations': 0,
        'average_completion_time': '2h 15m',
        'last_active': timestamp(hours_ago=1)
    },
    {
        'agent_id': 'agent_writer_002',
        'name': 'ScholarText Pro',
        'type': 'scientific_writing',
        'trust_score': 92,
        'reputation': 4.7,
        'total_operations': 120,
        'success_rate': 0.94,
        'security_incidents': 0,
        'policy_violations': 1,
        'average_completion_time': '45m',
        'last_active': timestamp(minutes_ago=30)
    },
    {
        'agent_id': 'agent_security_003',
        'name': 'BlockAudit Sentinel',
        'type': 'security_audit',
        'trust_score': 99,
        'reputation': 5.0,
        'total_operations': 200,
        'success_rate': 0.99,
        'security_incidents': 0,
        'policy_violations': 0,
        'average_completion_time': '1h 30m',
        'last_active': timestamp(hours_ago=4)
    },
    {
        'agent_id': 'agent_gov_004',
        'name': 'DAO Architect',
        'type': 'governance_design',
        'trust_score': 94,
        'reputation': 4.8,
        'total_operations': 55,
        'success_rate': 0.95,
        'security_incidents': 0,
        'policy_violations': 0,
        'average_completion_time': '3h',
        'last_active': timestamp(hours_ago=10)
    }
]

AGENT_TRUST_HISTORY = {
    'agent_research_001': [
        {'timestamp': timestamp(days_ago=30), 'score': 90},
        {'timestamp': timestamp(days_ago=15), 'score': 93},
        {'timestamp': timestamp(days_ago=1), 'score': 96}
    ]
}

# ============================================================================
# CAPABILITY REGISTRY
# ============================================================================

SAMPLE_CAPABILITIES = [
    {
        'capability_id': 'cap_research_paper',
        'capability_type': 'scientific_writing',
        'provider_id': 'agent_research_001',
        'provider_name': 'DeepScience AI',
        'name': 'Academic Paper Generation',
        'description': 'Generate LaTeX-formatted academic papers with proper citations',
        'trust_score': 96,
        'reputation': 4.9,
        'price': 120.0,
        'invocations': 80,
        'success_rate': 0.98,
        'tags': ['latex', 'academic', 'research', 'arxiv'],
        'created_at': timestamp(days_ago=90)
    },
    {
        'capability_id': 'cap_smart_contract_audit',
        'capability_type': 'security_audit',
        'provider_id': 'agent_security_003',
        'provider_name': 'BlockAudit Sentinel',
        'name': 'Solidity Smart Contract Audit',
        'description': 'Deep analysis of EVM smart contracts for vulnerabilities',
        'trust_score': 99,
        'reputation': 5.0,
        'price': 300.0,
        'invocations': 150,
        'success_rate': 0.99,
        'tags': ['solidity', 'security', 'audit', 'blockchain'],
        'created_at': timestamp(days_ago=120)
    }
]

# ============================================================================
# PROVIDERS (For Registry Service Compatibility)
# ============================================================================

SAMPLE_PROVIDERS = [
    {
        'provider_id': 'agent_research_001',
        'name': 'DeepScience AI',
        'description': 'Specialized in academic research and scientific writing.',
        'reputation': 4.9,
        'trust_score': 96
    },
    {
        'provider_id': 'agent_writer_002',
        'name': 'ScholarText Pro',
        'description': 'Expert technical and academic documentation services.',
        'reputation': 4.7,
        'trust_score': 92
    },
    {
        'provider_id': 'agent_security_003',
        'name': 'BlockAudit Sentinel',
        'description': 'Top-tier smart contract auditing and security analysis.',
        'reputation': 5.0,
        'trust_score': 99
    },
    {
        'provider_id': 'agent_gov_004',
        'name': 'DAO Architect',
        'description': 'Governance system design and implementation.',
        'reputation': 4.8,
        'trust_score': 94
    }
]

# ============================================================================
# GOVERNANCE DECISIONS
# ============================================================================

GOVERNANCE_DECISIONS = [
    {
        'decision_id': 'dec_001',
        'workflow_id': 'wf_mission_001',
        'stage': 'governance',
        'decision': 'approved',
        'timestamp': timestamp(days_ago=1, hours_ago=-1),
        'trust_score': 95.0,
        'policy_violations': 0,
        'reason': 'Auto-approved by policy (Score: 95 > Threshold: 90)'
    },
    {
        'decision_id': 'dec_002',
        'workflow_id': 'wf_mission_002',
        'stage': 'governance',
        'decision': 'approved',
        'timestamp': timestamp(days_ago=2),
        'trust_score': 88.0,
        'policy_violations': 0,
        'reason': 'Human approval granted via breakpoint: Risk accepted'
    },
    {
        'decision_id': 'dec_003',
        'workflow_id': 'wf_mission_003',
        'stage': 'execution',
        'decision': 'rejected',
        'timestamp': timestamp(days_ago=3),
        'trust_score': 72.0,
        'policy_violations': 1,
        'reason': 'Human rejected: Excessive cost deviation'
    },
    {
        'decision_id': 'dec_004',
        'workflow_id': 'wf_mission_004',
        'stage': 'governance',
        'decision': 'approved',
        'timestamp': timestamp(hours_ago=4),
        'trust_score': 98.0,
        'policy_violations': 0,
        'reason': 'Auto-approved by policy (Score: 98 > Threshold: 90)'
    },
    {
        'decision_id': 'dec_005',
        'workflow_id': 'wf_mission_005',
        'stage': 'governance',
        'decision': 'approved',
        'timestamp': timestamp(hours_ago=1),
        'trust_score': 92.0,
        'policy_violations': 0,
        'reason': 'Auto-approved by policy (Score: 92 > Threshold: 90)'
    }
]

# ============================================================================
# NETWORK PROVIDERS (Blockchain & Storage)
# ============================================================================

SAMPLE_NETWORK_PROVIDERS = [
    # --- PRODUCTION ---
    {
        'name': 'Ethereum Mainnet',
        'provider_type': 'EVM',
        'rpc_url': 'https://mainnet.infura.io/v3/YOUR_KEY',
        'chain_id': 1,
        'is_default': True,
        'meta_data': {
            'env': 'production',
            'explorer': 'https://etherscan.io',
            'badge_color': 'red'
        }
    },
    {
        'name': 'Filecoin Mainnet',
        'provider_type': 'FILECOIN',
        'rpc_url': 'https://api.node.glif.io',
        'is_default': True,
        'meta_data': {
            'env': 'production',
            'explorer': 'https://filfox.info/en',
            'badge_color': 'blue'
        }
    },

    # --- QA / STAGING ---
    {
        'name': 'Sepolia Testnet',
        'provider_type': 'EVM',
        'rpc_url': 'https://sepolia.infura.io/v3/YOUR_KEY',
        'chain_id': 11155111,
        'is_default': False,
        'meta_data': {
            'env': 'qa',
            'explorer': 'https://sepolia.etherscan.io',
            'badge_color': 'orange'
        }
    },
    {
        'name': 'IPFS Public Gateway',
        'provider_type': 'STORAGE',
        'rpc_url': 'https://ipfs.io',
        'is_default': True,
        'meta_data': {
            'env': 'qa',
            'gateway': True,
            'badge_color': 'orange'
        }
    },

    # --- DEVELOPMENT ---
    {
        'name': 'Local Hardhat',
        'provider_type': 'EVM',
        'rpc_url': 'http://127.0.0.1:8545',
        'chain_id': 31337,
        'is_default': False,
        'meta_data': {
            'env': 'development',
            'console_logs': True,
            'badge_color': 'green'
        }
    },
    {
        'name': 'Local IPFS Node',
        'provider_type': 'STORAGE',
        'rpc_url': 'http://127.0.0.1:5001',
        'is_default': False,
        'meta_data': {
            'env': 'development',
            'local': True,
            'badge_color': 'green'
        }
    }
]
