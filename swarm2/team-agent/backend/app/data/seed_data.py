"""
Seed data for Team Agent Platform UI.
Provides realistic sample data for all components.
"""
from datetime import datetime, timedelta
import random

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
        'description': 'Build a REST API for user authentication with JWT tokens, rate limiting, and password hashing',
        'required_capabilities': [
            {'capability_type': 'code_generation', 'min_trust_score': 80, 'max_cost': 100},
            {'capability_type': 'security_audit', 'min_trust_score': 90, 'max_cost': 50},
            {'capability_type': 'testing', 'min_trust_score': 75, 'max_cost': 30}
        ],
        'min_trust_score': 80,
        'max_cost': 200,
        'breakpoints': ['capability_selection', 'design_approval'],
        'auto_approve_trusted': True,
        'auto_approve_threshold': 90,
        'created_at': timestamp(days_ago=2)
    },
    {
        'mission_id': 'mission_002',
        'description': 'Analyze database performance and optimize slow queries in PostgreSQL',
        'required_capabilities': [
            {'capability_type': 'data_analysis', 'min_trust_score': 85, 'max_cost': 80},
            {'capability_type': 'code_review', 'min_trust_score': 80, 'max_cost': 40}
        ],
        'min_trust_score': 85,
        'max_cost': 150,
        'breakpoints': ['capability_selection'],
        'auto_approve_trusted': True,
        'auto_approve_threshold': 90,
        'created_at': timestamp(days_ago=1, hours_ago=5)
    },
    {
        'mission_id': 'mission_003',
        'description': 'Create comprehensive documentation for Python microservices architecture',
        'required_capabilities': [
            {'capability_type': 'documentation', 'min_trust_score': 75, 'max_cost': 60}
        ],
        'min_trust_score': 75,
        'max_cost': 100,
        'breakpoints': [],
        'auto_approve_trusted': True,
        'auto_approve_threshold': 85,
        'created_at': timestamp(hours_ago=8)
    },
    {
        'mission_id': 'mission_004',
        'description': 'Implement real-time websocket chat with message encryption',
        'required_capabilities': [
            {'capability_type': 'code_generation', 'min_trust_score': 85, 'max_cost': 120},
            {'capability_type': 'security_audit', 'min_trust_score': 95, 'max_cost': 60}
        ],
        'min_trust_score': 85,
        'max_cost': 200,
        'breakpoints': ['capability_selection', 'build_approval', 'review_approval'],
        'auto_approve_trusted': False,
        'auto_approve_threshold': 95,
        'created_at': timestamp(hours_ago=2)
    },
    {
        'mission_id': 'mission_005',
        'description': 'Deploy containerized application to Kubernetes with auto-scaling',
        'required_capabilities': [
            {'capability_type': 'deployment', 'min_trust_score': 90, 'max_cost': 100},
            {'capability_type': 'monitoring', 'min_trust_score': 85, 'max_cost': 40}
        ],
        'min_trust_score': 90,
        'max_cost': 180,
        'breakpoints': ['design_approval'],
        'auto_approve_trusted': True,
        'auto_approve_threshold': 92,
        'created_at': timestamp(minutes_ago=30)
    }
]

SAMPLE_WORKFLOWS = [
    {
        'workflow_id': 'mission_001',
        'mission_id': 'mission_001',
        'status': 'completed',
        'progress': 100,
        'current_stage': 'recorder',
        'created_at': timestamp(days_ago=2),
        'updated_at': timestamp(days_ago=2, hours_ago=-1),
        'stages': [
            {
                'stage_name': 'initializing',
                'status': 'completed',
                'started_at': timestamp(days_ago=2),
                'completed_at': timestamp(days_ago=2, minutes_ago=-5),
                'output': {'message': 'Workflow initialized successfully'}
            },
            {
                'stage_name': 'capability_selection',
                'status': 'completed',
                'started_at': timestamp(days_ago=2, minutes_ago=-5),
                'completed_at': timestamp(days_ago=2, minutes_ago=-8),
                'output': {'selected_providers': ['agent_coder_001', 'agent_security_003']}
            },
            {
                'stage_name': 'architect',
                'status': 'completed',
                'started_at': timestamp(days_ago=2, minutes_ago=-8),
                'completed_at': timestamp(days_ago=2, minutes_ago=-25),
                'output': {'design': 'REST API with FastAPI, JWT auth, bcrypt hashing'}
            },
            {
                'stage_name': 'builder',
                'status': 'completed',
                'started_at': timestamp(days_ago=2, minutes_ago=-25),
                'completed_at': timestamp(days_ago=2, minutes_ago=-45),
                'output': {'files_created': 8, 'lines_of_code': 450}
            },
            {
                'stage_name': 'critic',
                'status': 'completed',
                'started_at': timestamp(days_ago=2, minutes_ago=-45),
                'completed_at': timestamp(days_ago=2, minutes_ago=-55),
                'output': {'issues_found': 2, 'security_score': 95}
            },
            {
                'stage_name': 'governance',
                'status': 'completed',
                'started_at': timestamp(days_ago=2, minutes_ago=-55),
                'completed_at': timestamp(days_ago=2, hours_ago=-1),
                'output': {'policy_violations': 0, 'approved': True}
            },
            {
                'stage_name': 'recorder',
                'status': 'completed',
                'started_at': timestamp(days_ago=2, hours_ago=-1),
                'completed_at': timestamp(days_ago=2, hours_ago=-1, minutes_ago=-2),
                'output': {'manifest_signed': True, 'artifacts_count': 8}
            }
        ]
    },
    {
        'workflow_id': 'mission_002',
        'mission_id': 'mission_002',
        'status': 'running',
        'progress': 60,
        'current_stage': 'builder',
        'created_at': timestamp(days_ago=1, hours_ago=5),
        'updated_at': timestamp(minutes_ago=5),
        'stages': [
            {
                'stage_name': 'initializing',
                'status': 'completed',
                'started_at': timestamp(days_ago=1, hours_ago=5),
                'completed_at': timestamp(days_ago=1, hours_ago=5, minutes_ago=-3)
            },
            {
                'stage_name': 'capability_selection',
                'status': 'completed',
                'started_at': timestamp(days_ago=1, hours_ago=5, minutes_ago=-3),
                'completed_at': timestamp(days_ago=1, hours_ago=5, minutes_ago=-6)
            },
            {
                'stage_name': 'architect',
                'status': 'completed',
                'started_at': timestamp(days_ago=1, hours_ago=5, minutes_ago=-6),
                'completed_at': timestamp(days_ago=1, hours_ago=5, minutes_ago=-20)
            },
            {
                'stage_name': 'builder',
                'status': 'running',
                'started_at': timestamp(days_ago=1, hours_ago=5, minutes_ago=-20),
                'completed_at': None
            },
            {
                'stage_name': 'critic',
                'status': 'pending',
                'started_at': None,
                'completed_at': None
            }
        ]
    },
    {
        'workflow_id': 'mission_003',
        'mission_id': 'mission_003',
        'status': 'completed',
        'progress': 100,
        'current_stage': 'recorder',
        'created_at': timestamp(hours_ago=8),
        'updated_at': timestamp(hours_ago=7),
        'stages': [
            {
                'stage_name': 'initializing',
                'status': 'completed',
                'started_at': timestamp(hours_ago=8),
                'completed_at': timestamp(hours_ago=8, minutes_ago=-2)
            },
            {
                'stage_name': 'architect',
                'status': 'completed',
                'started_at': timestamp(hours_ago=8, minutes_ago=-2),
                'completed_at': timestamp(hours_ago=8, minutes_ago=-10)
            },
            {
                'stage_name': 'builder',
                'status': 'completed',
                'started_at': timestamp(hours_ago=8, minutes_ago=-10),
                'completed_at': timestamp(hours_ago=7, minutes_ago=-30)
            },
            {
                'stage_name': 'recorder',
                'status': 'completed',
                'started_at': timestamp(hours_ago=7, minutes_ago=-30),
                'completed_at': timestamp(hours_ago=7)
            }
        ]
    },
    {
        'workflow_id': 'mission_004',
        'mission_id': 'mission_004',
        'status': 'paused',
        'progress': 25,
        'current_stage': 'capability_selection',
        'created_at': timestamp(hours_ago=2),
        'updated_at': timestamp(hours_ago=2, minutes_ago=-5),
        'stages': [
            {
                'stage_name': 'initializing',
                'status': 'completed',
                'started_at': timestamp(hours_ago=2),
                'completed_at': timestamp(hours_ago=2, minutes_ago=-2)
            },
            {
                'stage_name': 'capability_selection',
                'status': 'paused',
                'started_at': timestamp(hours_ago=2, minutes_ago=-2),
                'completed_at': None
            }
        ]
    },
    {
        'workflow_id': 'mission_005',
        'mission_id': 'mission_005',
        'status': 'failed',
        'progress': 40,
        'current_stage': 'builder',
        'created_at': timestamp(minutes_ago=30),
        'updated_at': timestamp(minutes_ago=15),
        'stages': [
            {
                'stage_name': 'initializing',
                'status': 'completed',
                'started_at': timestamp(minutes_ago=30),
                'completed_at': timestamp(minutes_ago=28)
            },
            {
                'stage_name': 'architect',
                'status': 'completed',
                'started_at': timestamp(minutes_ago=28),
                'completed_at': timestamp(minutes_ago=20)
            },
            {
                'stage_name': 'builder',
                'status': 'failed',
                'started_at': timestamp(minutes_ago=20),
                'completed_at': timestamp(minutes_ago=15),
                'output': {'error': 'Kubernetes cluster not accessible'}
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
        'workflow_id': 'mission_004',
        'breakpoint_type': 'capability_selection',
        'status': 'pending',
        'created_at': timestamp(hours_ago=2, minutes_ago=-5),
        'options': [
            {
                'provider_id': 'agent_websocket_001',
                'capability_id': 'cap_websocket_realtime',
                'match_score': 0.95,
                'trust_score': 92,
                'price': 85.0,
                'details': {'experience': 'high', 'completion_rate': 0.94}
            },
            {
                'provider_id': 'agent_fullstack_002',
                'capability_id': 'cap_realtime_comm',
                'match_score': 0.88,
                'trust_score': 87,
                'price': 75.0,
                'details': {'experience': 'medium', 'completion_rate': 0.89}
            },
            {
                'provider_id': 'agent_backend_003',
                'capability_id': 'cap_socket_server',
                'match_score': 0.82,
                'trust_score': 95,
                'price': 95.0,
                'details': {'experience': 'high', 'completion_rate': 0.96}
            }
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
        'status': 'expiring_soon',  # Within 30 days
        'key_size': 2048,
        'signature_algorithm': 'SHA256-RSA'
    }
}

REVOKED_CERTIFICATES = [
    {
        'serial_number': 'E5F6A7B8C9D0',
        'domain': 'execution',
        'revoked_at': timestamp(days_ago=5),
        'reason': 'key_compromise',
        'revoked_by': 'admin'
    }
]

# ============================================================================
# TRUST SCORES & AGENTS
# ============================================================================

SAMPLE_AGENTS = [
    {
        'agent_id': 'agent_coder_001',
        'name': 'CodeMaster Pro',
        'type': 'code_generation',
        'trust_score': 94,
        'reputation': 4.8,
        'total_operations': 156,
        'success_rate': 0.94,
        'security_incidents': 0,
        'policy_violations': 1,
        'average_completion_time': '45m',
        'last_active': timestamp(hours_ago=2)
    },
    {
        'agent_id': 'agent_security_003',
        'name': 'SecureGuard AI',
        'type': 'security_audit',
        'trust_score': 98,
        'reputation': 4.9,
        'total_operations': 203,
        'success_rate': 0.97,
        'security_incidents': 0,
        'policy_violations': 0,
        'average_completion_time': '28m',
        'last_active': timestamp(hours_ago=1)
    },
    {
        'agent_id': 'agent_tester_005',
        'name': 'TestBot Elite',
        'type': 'testing',
        'trust_score': 89,
        'reputation': 4.5,
        'total_operations': 124,
        'success_rate': 0.89,
        'security_incidents': 1,
        'policy_violations': 2,
        'average_completion_time': '32m',
        'last_active': timestamp(hours_ago=5)
    },
    {
        'agent_id': 'agent_data_007',
        'name': 'DataWizard',
        'type': 'data_analysis',
        'trust_score': 92,
        'reputation': 4.7,
        'total_operations': 98,
        'success_rate': 0.92,
        'security_incidents': 0,
        'policy_violations': 1,
        'average_completion_time': '38m',
        'last_active': timestamp(hours_ago=3)
    },
    {
        'agent_id': 'agent_deploy_009',
        'name': 'DeployMaster',
        'type': 'deployment',
        'trust_score': 87,
        'reputation': 4.4,
        'total_operations': 67,
        'success_rate': 0.88,
        'security_incidents': 0,
        'policy_violations': 3,
        'average_completion_time': '52m',
        'last_active': timestamp(minutes_ago=30)
    },
    {
        'agent_id': 'agent_docs_011',
        'name': 'DocuGenius',
        'type': 'documentation',
        'trust_score': 85,
        'reputation': 4.3,
        'total_operations': 145,
        'success_rate': 0.91,
        'security_incidents': 0,
        'policy_violations': 2,
        'average_completion_time': '25m',
        'last_active': timestamp(hours_ago=7)
    }
]

# Trust history for detailed view
AGENT_TRUST_HISTORY = {
    'agent_coder_001': [
        {'timestamp': timestamp(days_ago=30), 'score': 88},
        {'timestamp': timestamp(days_ago=25), 'score': 89},
        {'timestamp': timestamp(days_ago=20), 'score': 90},
        {'timestamp': timestamp(days_ago=15), 'score': 92},
        {'timestamp': timestamp(days_ago=10), 'score': 93},
        {'timestamp': timestamp(days_ago=5), 'score': 93},
        {'timestamp': timestamp(days_ago=1), 'score': 94}
    ],
    'agent_security_003': [
        {'timestamp': timestamp(days_ago=30), 'score': 95},
        {'timestamp': timestamp(days_ago=25), 'score': 96},
        {'timestamp': timestamp(days_ago=20), 'score': 96},
        {'timestamp': timestamp(days_ago=15), 'score': 97},
        {'timestamp': timestamp(days_ago=10), 'score': 97},
        {'timestamp': timestamp(days_ago=5), 'score': 98},
        {'timestamp': timestamp(days_ago=1), 'score': 98}
    ]
}

# ============================================================================
# CAPABILITY REGISTRY
# ============================================================================

SAMPLE_CAPABILITIES = [
    # Code Generation
    {
        'capability_id': 'cap_python_api',
        'capability_type': 'code_generation',
        'provider_id': 'agent_coder_001',
        'provider_name': 'CodeMaster Pro',
        'name': 'Python REST API Development',
        'description': 'Build production-ready REST APIs with FastAPI or Flask',
        'trust_score': 94,
        'reputation': 4.8,
        'price': 85.0,
        'invocations': 45,
        'success_rate': 0.94,
        'tags': ['python', 'rest', 'api', 'fastapi', 'flask'],
        'created_at': timestamp(days_ago=60)
    },
    {
        'capability_id': 'cap_react_frontend',
        'capability_type': 'code_generation',
        'provider_id': 'agent_frontend_002',
        'provider_name': 'ReactBuilder AI',
        'name': 'React Application Development',
        'description': 'Build modern React applications with TypeScript and state management',
        'trust_score': 91,
        'reputation': 4.6,
        'price': 90.0,
        'invocations': 38,
        'success_rate': 0.91,
        'tags': ['react', 'typescript', 'frontend', 'redux'],
        'created_at': timestamp(days_ago=45)
    },
    {
        'capability_id': 'cap_nodejs_microservice',
        'capability_type': 'code_generation',
        'provider_id': 'agent_backend_003',
        'provider_name': 'MicroService Expert',
        'name': 'Node.js Microservices',
        'description': 'Design and implement scalable microservices with Node.js',
        'trust_score': 93,
        'reputation': 4.7,
        'price': 100.0,
        'invocations': 32,
        'success_rate': 0.93,
        'tags': ['nodejs', 'microservices', 'express', 'nestjs'],
        'created_at': timestamp(days_ago=50)
    },

    # Security Audit
    {
        'capability_id': 'cap_security_scan',
        'capability_type': 'security_audit',
        'provider_id': 'agent_security_003',
        'provider_name': 'SecureGuard AI',
        'name': 'Comprehensive Security Audit',
        'description': 'OWASP Top 10 scanning, dependency analysis, code review',
        'trust_score': 98,
        'reputation': 4.9,
        'price': 65.0,
        'invocations': 67,
        'success_rate': 0.97,
        'tags': ['security', 'owasp', 'audit', 'vulnerability'],
        'created_at': timestamp(days_ago=90)
    },
    {
        'capability_id': 'cap_penetration_test',
        'capability_type': 'security_audit',
        'provider_id': 'agent_pentest_004',
        'provider_name': 'PenTest Master',
        'name': 'Penetration Testing',
        'description': 'Ethical hacking and penetration testing for web applications',
        'trust_score': 96,
        'reputation': 4.8,
        'price': 120.0,
        'invocations': 24,
        'success_rate': 0.96,
        'tags': ['pentest', 'security', 'hacking', 'vulnerability'],
        'created_at': timestamp(days_ago=70)
    },

    # Testing
    {
        'capability_id': 'cap_unit_testing',
        'capability_type': 'testing',
        'provider_id': 'agent_tester_005',
        'provider_name': 'TestBot Elite',
        'name': 'Automated Test Suite Generation',
        'description': 'Create comprehensive unit and integration tests',
        'trust_score': 89,
        'reputation': 4.5,
        'price': 45.0,
        'invocations': 38,
        'success_rate': 0.89,
        'tags': ['testing', 'pytest', 'unittest', 'coverage'],
        'created_at': timestamp(days_ago=55)
    },
    {
        'capability_id': 'cap_e2e_testing',
        'capability_type': 'testing',
        'provider_id': 'agent_qa_006',
        'provider_name': 'QA Automation Pro',
        'name': 'End-to-End Testing',
        'description': 'Automated E2E tests with Playwright and Cypress',
        'trust_score': 90,
        'reputation': 4.6,
        'price': 55.0,
        'invocations': 29,
        'success_rate': 0.90,
        'tags': ['e2e', 'playwright', 'cypress', 'automation'],
        'created_at': timestamp(days_ago=40)
    },

    # Data Analysis
    {
        'capability_id': 'cap_sql_optimize',
        'capability_type': 'data_analysis',
        'provider_id': 'agent_data_007',
        'provider_name': 'DataWizard',
        'name': 'Database Query Optimization',
        'description': 'Analyze and optimize SQL queries for PostgreSQL/MySQL',
        'trust_score': 92,
        'reputation': 4.7,
        'price': 75.0,
        'invocations': 29,
        'success_rate': 0.92,
        'tags': ['database', 'sql', 'performance', 'postgresql'],
        'created_at': timestamp(days_ago=65)
    },
    {
        'capability_id': 'cap_data_visualization',
        'capability_type': 'data_analysis',
        'provider_id': 'agent_viz_008',
        'provider_name': 'VisualizerBot',
        'name': 'Data Visualization',
        'description': 'Create interactive dashboards with D3.js and Chart.js',
        'trust_score': 88,
        'reputation': 4.4,
        'price': 60.0,
        'invocations': 26,
        'success_rate': 0.88,
        'tags': ['visualization', 'd3', 'charts', 'dashboard'],
        'created_at': timestamp(days_ago=35)
    },

    # Deployment
    {
        'capability_id': 'cap_k8s_deploy',
        'capability_type': 'deployment',
        'provider_id': 'agent_deploy_009',
        'provider_name': 'DeployMaster',
        'name': 'Kubernetes Deployment',
        'description': 'Deploy and configure applications on Kubernetes clusters',
        'trust_score': 87,
        'reputation': 4.4,
        'price': 95.0,
        'invocations': 22,
        'success_rate': 0.88,
        'tags': ['kubernetes', 'docker', 'containers', 'deployment'],
        'created_at': timestamp(days_ago=48)
    },
    {
        'capability_id': 'cap_aws_deploy',
        'capability_type': 'deployment',
        'provider_id': 'agent_cloud_010',
        'provider_name': 'CloudDeploy AI',
        'name': 'AWS Infrastructure Deployment',
        'description': 'Deploy and manage infrastructure on AWS with Terraform',
        'trust_score': 91,
        'reputation': 4.6,
        'price': 110.0,
        'invocations': 31,
        'success_rate': 0.91,
        'tags': ['aws', 'terraform', 'infrastructure', 'iac'],
        'created_at': timestamp(days_ago=52)
    },

    # Documentation
    {
        'capability_id': 'cap_api_docs',
        'capability_type': 'documentation',
        'provider_id': 'agent_docs_011',
        'provider_name': 'DocuGenius',
        'name': 'API Documentation Generation',
        'description': 'Generate OpenAPI/Swagger documentation for REST APIs',
        'trust_score': 85,
        'reputation': 4.3,
        'price': 40.0,
        'invocations': 45,
        'success_rate': 0.91,
        'tags': ['documentation', 'openapi', 'swagger', 'api'],
        'created_at': timestamp(days_ago=58)
    },
    {
        'capability_id': 'cap_user_guides',
        'capability_type': 'documentation',
        'provider_id': 'agent_writer_012',
        'provider_name': 'TechWriter Pro',
        'name': 'User Guide & Tutorial Creation',
        'description': 'Write comprehensive user guides and tutorials',
        'trust_score': 83,
        'reputation': 4.2,
        'price': 35.0,
        'invocations': 38,
        'success_rate': 0.89,
        'tags': ['documentation', 'tutorial', 'guide', 'markdown'],
        'created_at': timestamp(days_ago=42)
    },

    # Code Review
    {
        'capability_id': 'cap_code_review',
        'capability_type': 'code_review',
        'provider_id': 'agent_reviewer_013',
        'provider_name': 'CodeCritic AI',
        'name': 'Comprehensive Code Review',
        'description': 'In-depth code review for quality, performance, and best practices',
        'trust_score': 95,
        'reputation': 4.8,
        'price': 70.0,
        'invocations': 53,
        'success_rate': 0.95,
        'tags': ['review', 'quality', 'best-practices', 'refactoring'],
        'created_at': timestamp(days_ago=75)
    },

    # Monitoring
    {
        'capability_id': 'cap_observability',
        'capability_type': 'monitoring',
        'provider_id': 'agent_monitor_014',
        'provider_name': 'ObservabilityBot',
        'name': 'Application Observability Setup',
        'description': 'Set up monitoring with Prometheus, Grafana, and ELK stack',
        'trust_score': 89,
        'reputation': 4.5,
        'price': 80.0,
        'invocations': 27,
        'success_rate': 0.89,
        'tags': ['monitoring', 'prometheus', 'grafana', 'observability'],
        'created_at': timestamp(days_ago=38)
    },

    # Refactoring
    {
        'capability_id': 'cap_refactor',
        'capability_type': 'refactoring',
        'provider_id': 'agent_refactor_015',
        'provider_name': 'RefactorMaster',
        'name': 'Code Refactoring & Optimization',
        'description': 'Refactor legacy code for better maintainability and performance',
        'trust_score': 92,
        'reputation': 4.7,
        'price': 90.0,
        'invocations': 34,
        'success_rate': 0.92,
        'tags': ['refactoring', 'optimization', 'clean-code', 'legacy'],
        'created_at': timestamp(days_ago=62)
    },

    # Database Design
    {
        'capability_id': 'cap_db_design',
        'capability_type': 'database_design',
        'provider_id': 'agent_dbarch_016',
        'provider_name': 'DatabaseArchitect',
        'name': 'Database Schema Design',
        'description': 'Design normalized database schemas with ER diagrams',
        'trust_score': 93,
        'reputation': 4.7,
        'price': 85.0,
        'invocations': 25,
        'success_rate': 0.93,
        'tags': ['database', 'schema', 'er-diagram', 'normalization'],
        'created_at': timestamp(days_ago=67)
    },

    # Performance Optimization
    {
        'capability_id': 'cap_perf_opt',
        'capability_type': 'performance_optimization',
        'provider_id': 'agent_perf_017',
        'provider_name': 'PerformanceGuru',
        'name': 'Application Performance Tuning',
        'description': 'Profile and optimize application performance bottlenecks',
        'trust_score': 94,
        'reputation': 4.8,
        'price': 95.0,
        'invocations': 21,
        'success_rate': 0.94,
        'tags': ['performance', 'profiling', 'optimization', 'benchmarking'],
        'created_at': timestamp(days_ago=44)
    },

    # CI/CD
    {
        'capability_id': 'cap_cicd_pipeline',
        'capability_type': 'cicd',
        'provider_id': 'agent_devops_018',
        'provider_name': 'DevOps Automation',
        'name': 'CI/CD Pipeline Setup',
        'description': 'Configure GitHub Actions, GitLab CI, or Jenkins pipelines',
        'trust_score': 90,
        'reputation': 4.6,
        'price': 75.0,
        'invocations': 36,
        'success_rate': 0.90,
        'tags': ['cicd', 'github-actions', 'jenkins', 'automation'],
        'created_at': timestamp(days_ago=51)
    },

    # API Integration
    {
        'capability_id': 'cap_api_integration',
        'capability_type': 'api_integration',
        'provider_id': 'agent_integrator_019',
        'provider_name': 'APIConnector',
        'name': 'Third-Party API Integration',
        'description': 'Integrate with payment gateways, social media, and SaaS APIs',
        'trust_score': 88,
        'reputation': 4.5,
        'price': 70.0,
        'invocations': 33,
        'success_rate': 0.88,
        'tags': ['api', 'integration', 'rest', 'webhooks'],
        'created_at': timestamp(days_ago=46)
    },

    # Machine Learning
    {
        'capability_id': 'cap_ml_model',
        'capability_type': 'machine_learning',
        'provider_id': 'agent_ml_020',
        'provider_name': 'MLEngineer AI',
        'name': 'ML Model Development',
        'description': 'Build and train machine learning models with scikit-learn and TensorFlow',
        'trust_score': 91,
        'reputation': 4.6,
        'price': 130.0,
        'invocations': 18,
        'success_rate': 0.91,
        'tags': ['machine-learning', 'tensorflow', 'scikit-learn', 'ai'],
        'created_at': timestamp(days_ago=33)
    }
]

# Provider information
SAMPLE_PROVIDERS = [
    {'provider_id': 'agent_coder_001', 'name': 'CodeMaster Pro', 'type': 'code_generation', 'trust_score': 94, 'total_capabilities': 1},
    {'provider_id': 'agent_frontend_002', 'name': 'ReactBuilder AI', 'type': 'code_generation', 'trust_score': 91, 'total_capabilities': 1},
    {'provider_id': 'agent_backend_003', 'name': 'MicroService Expert', 'type': 'code_generation', 'trust_score': 93, 'total_capabilities': 1},
    {'provider_id': 'agent_security_003', 'name': 'SecureGuard AI', 'type': 'security_audit', 'trust_score': 98, 'total_capabilities': 1},
    {'provider_id': 'agent_pentest_004', 'name': 'PenTest Master', 'type': 'security_audit', 'trust_score': 96, 'total_capabilities': 1},
    {'provider_id': 'agent_tester_005', 'name': 'TestBot Elite', 'type': 'testing', 'trust_score': 89, 'total_capabilities': 1},
    {'provider_id': 'agent_qa_006', 'name': 'QA Automation Pro', 'type': 'testing', 'trust_score': 90, 'total_capabilities': 1},
    {'provider_id': 'agent_data_007', 'name': 'DataWizard', 'type': 'data_analysis', 'trust_score': 92, 'total_capabilities': 1},
    {'provider_id': 'agent_viz_008', 'name': 'VisualizerBot', 'type': 'data_analysis', 'trust_score': 88, 'total_capabilities': 1},
    {'provider_id': 'agent_deploy_009', 'name': 'DeployMaster', 'type': 'deployment', 'trust_score': 87, 'total_capabilities': 1},
    {'provider_id': 'agent_cloud_010', 'name': 'CloudDeploy AI', 'type': 'deployment', 'trust_score': 91, 'total_capabilities': 1},
    {'provider_id': 'agent_docs_011', 'name': 'DocuGenius', 'type': 'documentation', 'trust_score': 85, 'total_capabilities': 1},
    {'provider_id': 'agent_writer_012', 'name': 'TechWriter Pro', 'type': 'documentation', 'trust_score': 83, 'total_capabilities': 1},
    {'provider_id': 'agent_reviewer_013', 'name': 'CodeCritic AI', 'type': 'code_review', 'trust_score': 95, 'total_capabilities': 1},
    {'provider_id': 'agent_monitor_014', 'name': 'ObservabilityBot', 'type': 'monitoring', 'trust_score': 89, 'total_capabilities': 1},
    {'provider_id': 'agent_refactor_015', 'name': 'RefactorMaster', 'type': 'refactoring', 'trust_score': 92, 'total_capabilities': 1},
    {'provider_id': 'agent_dbarch_016', 'name': 'DatabaseArchitect', 'type': 'database_design', 'trust_score': 93, 'total_capabilities': 1},
    {'provider_id': 'agent_perf_017', 'name': 'PerformanceGuru', 'type': 'performance_optimization', 'trust_score': 94, 'total_capabilities': 1},
    {'provider_id': 'agent_devops_018', 'name': 'DevOps Automation', 'type': 'cicd', 'trust_score': 90, 'total_capabilities': 1},
    {'provider_id': 'agent_integrator_019', 'name': 'APIConnector', 'type': 'api_integration', 'trust_score': 88, 'total_capabilities': 1},
    {'provider_id': 'agent_ml_020', 'name': 'MLEngineer AI', 'type': 'machine_learning', 'trust_score': 91, 'total_capabilities': 1}
]

# ============================================================================
# GOVERNANCE & POLICY
# ============================================================================

GOVERNANCE_CONFIG = {
    'min_trust_score': 75,
    'require_security_review': True,
    'allowed_languages': ['python', 'javascript', 'typescript', 'go', 'rust'],
    'max_cost_per_mission': 500,
    'require_code_review': True,
    'auto_approve_threshold': 90,
    'enable_breakpoints': True
}

GOVERNANCE_DECISIONS = [
    {
        'decision_id': 'dec_001',
        'workflow_id': 'mission_001',
        'stage': 'governance',
        'decision': 'approved',
        'timestamp': timestamp(days_ago=2, hours_ago=-1),
        'trust_score': 94,
        'policy_violations': 0,
        'reason': 'All policies satisfied, high trust score'
    },
    {
        'decision_id': 'dec_002',
        'workflow_id': 'mission_003',
        'stage': 'governance',
        'decision': 'approved',
        'timestamp': timestamp(hours_ago=7),
        'trust_score': 85,
        'policy_violations': 0,
        'reason': 'Documentation task, low risk'
    },
    {
        'decision_id': 'dec_003',
        'workflow_id': 'mission_005',
        'stage': 'governance',
        'decision': 'rejected',
        'timestamp': timestamp(minutes_ago=20),
        'trust_score': 87,
        'policy_violations': 1,
        'reason': 'Deployment requires manual approval'
    }
]

# ============================================================================
# ARTIFACTS & MANIFESTS
# ============================================================================

SAMPLE_MANIFESTS = {
    'mission_001': {
        'workflow_id': 'mission_001',
        'mission_id': 'mission_001',
        'generated_at': timestamp(days_ago=2, hours_ago=-1, minutes_ago=-2),
        'signatures': {
            'architect': 'SHA256:a1b2c3d4...',
            'builder': 'SHA256:e5f6g7h8...',
            'critic': 'SHA256:i9j0k1l2...',
            'governance': 'SHA256:m3n4o5p6...',
            'recorder': 'SHA256:q7r8s9t0...'
        },
        'checksums': {
            'auth_api.py': 'SHA256:1a2b3c4d...',
            'jwt_utils.py': 'SHA256:5e6f7g8h...',
            'rate_limiter.py': 'SHA256:9i0j1k2l...'
        },
        'artifact_count': 8,
        'total_size': 45678
    },
    'mission_003': {
        'workflow_id': 'mission_003',
        'mission_id': 'mission_003',
        'generated_at': timestamp(hours_ago=7),
        'signatures': {
            'architect': 'SHA256:u1v2w3x4...',
            'builder': 'SHA256:y5z6a7b8...',
            'recorder': 'SHA256:c9d0e1f2...'
        },
        'checksums': {
            'README.md': 'SHA256:g3h4i5j6...',
            'API_DOCS.md': 'SHA256:k7l8m9n0...',
            'ARCHITECTURE.md': 'SHA256:o1p2q3r4...'
        },
        'artifact_count': 5,
        'total_size': 23456
    }
}
