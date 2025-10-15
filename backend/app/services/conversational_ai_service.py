"""
Conversational AI Service for Interactive SDLC Guidance
This service provides intelligent, context-aware assistance throughout the SDLC
"""
from typing import Dict, Any, List, Optional
import json
import re

class ConversationalAIService:
    def __init__(self):
        self.context_memory = {}
        self.current_phase_prompts = {
            1: self._get_phase1_prompts(),
            2: self._get_phase2_prompts(),
            3: self._get_phase3_prompts(),
            4: self._get_phase4_prompts(),
            5: self._get_phase5_prompts(),
            6: self._get_phase6_prompts()
        }
    
    def process_conversational_query(
        self, 
        query: str, 
        project_context: Dict[str, Any],
        phase_id: int,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Process user query in a conversational manner and provide intelligent responses
        """
        # Detect intent
        intent = self._detect_intent(query, phase_id)
        
        # Get phase-specific context
        phase_context = project_context.get('phases', {}).get(str(phase_id), {})
        
        # Generate response based on intent
        if intent == "create_project":
            return self._guide_project_creation(query, project_context)
        elif intent == "start_phase":
            return self._guide_phase_start(phase_id, project_context)
        elif intent == "generate_content":
            return self._generate_phase_content(query, phase_id, project_context)
        elif intent == "review_approval":
            return self._guide_approval_process(phase_id, project_context)
        elif intent == "next_steps":
            return self._suggest_next_steps(phase_id, project_context)
        else:
            return self._provide_contextual_help(query, phase_id, project_context)
    
    def _detect_intent(self, query: str, phase_id: int) -> str:
        """Detect user intent from query"""
        query_lower = query.lower()
        
        # Project creation
        if any(keyword in query_lower for keyword in ['create project', 'new project', 'start project', 'trucking']):
            return "create_project"
        
        # Phase start
        if any(keyword in query_lower for keyword in ['start phase', 'begin phase', 'move to phase']):
            return "start_phase"
        
        # Content generation
        if any(keyword in query_lower for keyword in ['generate', 'create prd', 'create brd', 'write', 'design']):
            return "generate_content"
        
        # Approval
        if any(keyword in query_lower for keyword in ['approval', 'review', 'stakeholder']):
            return "review_approval"
        
        # Next steps
        if any(keyword in query_lower for keyword in ['next', 'what should', 'what do']):
            return "next_steps"
        
        return "help"
    
    def _guide_project_creation(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Guide user through project creation"""
        
        # Check if trucking project mentioned
        is_trucking = 'truck' in query.lower()
        
        if is_trucking:
            return {
                "response": """🚚 Great! Let's create a Zero-Emission Trucking project!

I'll help you set this up. Here's what I understand:

**Project: Zero-Emission Trucking Platform**
- Focus: Modernizing logistics in the automobile industry
- Key Features: Zero-emission trucks (ZETs) + Advanced fleet management

Let me ask a few questions to get started:

1️⃣ **What's your primary goal?**
   - Develop ZET vehicles
   - Build fleet management software
   - Both vehicle and software platform

2️⃣ **Target timeline?**
   - 6 months (MVP)
   - 12 months (Full release)
   - 18+ months (Enterprise solution)

3️⃣ **Key stakeholders?**
   - Product team
   - Engineering team
   - Business stakeholders
   - Regulatory/Compliance team

Just respond naturally, and I'll create the project structure for you! 🎯""",
                "confidence_score": 95,
                "action": "await_user_input",
                "suggested_responses": [
                    "Both vehicle and software platform, 12 months timeline",
                    "Fleet management software, 6 months MVP",
                    "Full enterprise solution with all teams involved"
                ],
                "artifacts": {
                    "project_template": {
                        "name": "Zero-Emission Trucking Platform",
                        "description": "A trucking project in the automobile industry focusing on modernizing logistics through zero-emission trucks and advanced fleet management software",
                        "industry": "Automobile/Logistics",
                        "type": "Vehicle + Software Platform"
                    }
                }
            }
        else:
            return {
                "response": """👋 I'll help you create a new project!

To get started, I need to understand your project better. Tell me:

1. **What are you building?** (e.g., mobile app, web platform, IoT system)
2. **What problem does it solve?**
3. **Who are the users?**
4. **Any specific industry?** (e.g., healthcare, fintech, logistics)

You can answer in any format - I'll understand! 😊

**Example:** "I want to build a trucking platform for zero-emission vehicles with fleet management"
""",
                "confidence_score": 85,
                "action": "await_user_input",
                "suggested_responses": [
                    "Healthcare app for patient management",
                    "E-commerce platform with AI recommendations",
                    "IoT system for smart buildings"
                ]
            }
    
    def _guide_phase_start(self, phase_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Guide user through starting a phase"""
        
        prompts = self.current_phase_prompts.get(phase_id, {})
        
        return {
            "response": f"""✨ Let's start **{prompts['name']}**!

{prompts['description']}

**What we'll accomplish:**
{self._format_list(prompts['key_activities'])}

**Deliverables:**
{self._format_list(prompts['deliverables'])}

**I can help you with:**
{self._format_list(prompts['ai_assistance'])}

What would you like to start with? Just tell me naturally! 🎯""",
            "confidence_score": 90,
            "action": "await_user_input",
            "phase_id": phase_id,
            "artifacts": prompts
        }
    
    def _generate_phase_content(self, query: str, phase_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate phase-specific content"""
        
        if phase_id == 1:
            return self._generate_requirements(query, context)
        elif phase_id == 2:
            return self._generate_backlog(query, context)
        elif phase_id == 3:
            return self._generate_architecture(query, context)
        elif phase_id == 4:
            return self._generate_detailed_design(query, context)
        elif phase_id == 5:
            return self._generate_code_tests(query, context)
        elif phase_id == 6:
            return self._generate_deployment_plan(query, context)
    
    def _generate_requirements(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Phase 1 content - Requirements"""
        
        project_name = context.get('project_name', 'Your Project')
        project_desc = context.get('description', '')
        
        # For trucking project
        if 'truck' in project_desc.lower():
            prd_content = """# Product Requirements Document (PRD)
## Zero-Emission Trucking Platform

### 1. Executive Summary
Develop a comprehensive platform for zero-emission trucking operations, combining electric vehicle technology with advanced fleet management software.

### 2. Product Vision
Transform the logistics industry by providing sustainable, efficient, and cost-effective trucking solutions through zero-emission vehicles and AI-powered fleet management.

### 3. Target Users
- **Fleet Operators**: Companies managing truck fleets
- **Drivers**: Professional truck drivers
- **Logistics Managers**: Route and load planners
- **Maintenance Teams**: Vehicle maintenance staff
- **Business Analysts**: Performance monitoring

### 4. Core Features

#### 4.1 Zero-Emission Truck (ZET) Management
- Real-time battery monitoring
- Charging station locator and scheduling
- Range prediction and optimization
- Vehicle health monitoring
- Predictive maintenance alerts

#### 4.2 Fleet Management
- Real-time GPS tracking
- Route optimization
- Load management
- Driver assignment
- Fuel/Energy cost tracking
- Performance analytics

#### 4.3 Driver Portal
- Mobile app for drivers
- Route guidance
- Delivery confirmation
- Digital documentation
- Communication tools

#### 4.4 Analytics Dashboard
- Fleet performance metrics
- Cost analysis
- Environmental impact reporting
- Operational efficiency KPIs
- Predictive analytics

### 5. Technical Requirements
- Cloud-based architecture (AWS/Azure)
- Real-time data processing
- Mobile apps (iOS/Android)
- Web dashboard (React)
- API integration capabilities
- IoT device connectivity

### 6. Success Metrics
- 30% reduction in operational costs
- 100% zero-emission fleet
- 95% on-time delivery rate
- 50% reduction in maintenance costs
- 99.9% system uptime

### 7. Constraints
- Regulatory compliance (EPA, DOT)
- Data security and privacy (GDPR)
- Integration with existing systems
- Budget: $2.5M
- Timeline: 12 months
"""

            brd_content = """# Business Requirements Document (BRD)
## Zero-Emission Trucking Platform

### 1. Business Context
The logistics industry faces increasing pressure to reduce carbon emissions while maintaining cost efficiency. This platform addresses both concerns by enabling zero-emission operations with optimized fleet management.

### 2. Business Objectives
1. **Environmental**: Achieve 100% zero-emission operations
2. **Financial**: Reduce operational costs by 30%
3. **Efficiency**: Improve delivery performance by 20%
4. **Market**: Capture 15% market share in sustainable logistics

### 3. Stakeholders
- **CEO/Business Owner**: Strategic direction
- **CFO**: Financial oversight
- **COO**: Operational implementation
- **Fleet Managers**: Daily operations
- **Drivers**: End users
- **Customers**: Service recipients
- **Regulatory Bodies**: Compliance

### 4. Business Rules
1. All vehicles must be zero-emission
2. Driver hours must comply with DOT regulations
3. Vehicles must undergo maintenance every 10,000 miles
4. Real-time tracking must be available 24/7
5. Data retention: 7 years for compliance

### 5. Scope
**In Scope:**
- ZET vehicle management
- Fleet operations software
- Driver mobile app
- Analytics platform
- Integration APIs

**Out of Scope:**
- Vehicle manufacturing
- Charging infrastructure installation
- Third-party logistics services

### 6. Budget & Resources
- **Total Budget**: $2.5M
- **Development**: $1.5M
- **Infrastructure**: $500K
- **Operations**: $300K
- **Contingency**: $200K

**Team:**
- Project Manager: 1
- Backend Developers: 3
- Frontend Developers: 2
- Mobile Developers: 2
- DevOps: 1
- QA Engineers: 2
- UX/UI Designer: 1

### 7. Timeline
- Phase 1-2: 2 months (Requirements & Planning)
- Phase 3: 2 months (Architecture)
- Phase 4: 2 months (Detailed Design)
- Phase 5: 4 months (Development & Testing)
- Phase 6: 2 months (Deployment & Stabilization)

**Total: 12 months**

### 8. Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Battery technology limitations | Medium | High | Partner with leading EV manufacturers |
| Regulatory changes | Low | High | Regular compliance reviews |
| Integration complexity | High | Medium | Phased integration approach |
| Market adoption | Medium | High | Pilot program with key customers |

### 9. Success Criteria
- Platform deployed to production
- 100 vehicles onboarded in first year
- 95% user satisfaction score
- ROI positive within 18 months
"""

            return {
                "response": """✅ I've generated comprehensive requirements for your Zero-Emission Trucking Platform!

**📄 Product Requirements Document (PRD)**
- Executive Summary
- Core Features (ZET Management, Fleet Management, Driver Portal, Analytics)
- Technical Requirements
- Success Metrics

**📊 Business Requirements Document (BRD)**
- Business Context & Objectives
- Stakeholders & Business Rules
- Budget: $2.5M over 12 months
- Team Structure (12 people)
- Risk Assessment

**💡 Key Highlights:**
✅ 30% cost reduction target
✅ 100% zero-emission operations
✅ Real-time tracking & analytics
✅ Mobile-first approach

**What would you like to do next?**
1. Review and refine these documents
2. Add more specific requirements
3. Move to Phase 2 (Planning & Backlog)
4. Set up stakeholder approvals

The documents are ready in the sidebar! 👉""",
                "confidence_score": 92,
                "action": "content_generated",
                "artifacts": {
                    "prd": prd_content,
                    "brd": brd_content,
                    "type": "requirements_documents"
                },
                "suggested_actions": [
                    "Review PRD/BRD",
                    "Refine requirements",
                    "Move to Phase 2",
                    "Setup approvals"
                ]
            }
        
        return {
            "response": f"""📝 Let me generate requirements for {project_name}!

To create comprehensive PRD and BRD, I need a bit more context:

1. **Core features** - What are the main capabilities?
2. **Users** - Who will use this?
3. **Business goals** - What's the success criteria?

Tell me more about your project!""",
            "confidence_score": 75,
            "action": "await_user_input"
        }
    
    def _generate_backlog(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Phase 2 content - Backlog"""
        
        if 'truck' in context.get('description', '').lower():
            epics = [
                {
                    "title": "Zero-Emission Vehicle Management",
                    "description": "Complete system for managing electric trucks including battery monitoring, charging, and maintenance",
                    "stories": 15,
                    "points": 55,
                    "priority": "High",
                    "user_stories": [
                        "As a fleet manager, I want to monitor battery levels in real-time",
                        "As a driver, I want to find nearby charging stations",
                        "As a maintenance team, I want to receive predictive maintenance alerts",
                        "As an operator, I want to schedule charging during off-peak hours",
                        "As a manager, I want to track energy consumption per vehicle"
                    ]
                },
                {
                    "title": "Fleet Operations & Tracking",
                    "description": "Real-time tracking, route optimization, and operational management",
                    "stories": 20,
                    "points": 75,
                    "priority": "High",
                    "user_stories": [
                        "As a dispatcher, I want to track all vehicles in real-time",
                        "As a logistics manager, I want optimized route suggestions",
                        "As an operator, I want to assign drivers to vehicles",
                        "As a manager, I want to monitor delivery performance",
                        "As a customer, I want to track my shipment location"
                    ]
                },
                {
                    "title": "Driver Mobile Application",
                    "description": "Mobile app for drivers with route guidance, delivery confirmation, and communication",
                    "stories": 12,
                    "points": 40,
                    "priority": "High",
                    "user_stories": [
                        "As a driver, I want turn-by-turn navigation",
                        "As a driver, I want to confirm deliveries digitally",
                        "As a driver, I want to communicate with dispatch",
                        "As a driver, I want to see my schedule",
                        "As a driver, I want to report vehicle issues"
                    ]
                },
                {
                    "title": "Analytics & Reporting Dashboard",
                    "description": "Comprehensive analytics for fleet performance, costs, and environmental impact",
                    "stories": 18,
                    "points": 65,
                    "priority": "Medium",
                    "user_stories": [
                        "As a manager, I want to see fleet performance KPIs",
                        "As a CFO, I want cost analysis reports",
                        "As an operator, I want environmental impact metrics",
                        "As an analyst, I want predictive analytics",
                        "As a stakeholder, I want custom reports"
                    ]
                }
            ]
            
            sprint_plan = {
                "total_sprints": 8,
                "sprint_duration": "2 weeks",
                "team_velocity": 30,
                "total_points": 235,
                "sprints": [
                    {"number": 1, "focus": "Vehicle Management - Battery & Charging", "points": 30},
                    {"number": 2, "focus": "Vehicle Management - Maintenance & Monitoring", "points": 25},
                    {"number": 3, "focus": "Fleet Tracking - Real-time Location", "points": 30},
                    {"number": 4, "focus": "Fleet Operations - Route Optimization", "points": 30},
                    {"number": 5, "focus": "Driver App - Core Features", "points": 25},
                    {"number": 6, "focus": "Driver App - Advanced Features", "points": 15},
                    {"number": 7, "focus": "Analytics Dashboard - Core Metrics", "points": 30},
                    {"number": 8, "focus": "Analytics Dashboard - Advanced Reports", "points": 35}
                ]
            }
            
            return {
                "response": """✅ I've created a comprehensive Product Backlog for your Trucking Platform!

**📊 Backlog Summary:**
- **4 Epics** covering all major features
- **65 User Stories** broken down and ready
- **235 Story Points** estimated
- **8 Sprints** planned (2-week cycles)

**🎯 Epics Created:**

1️⃣ **Zero-Emission Vehicle Management** (55 pts, High Priority)
   - Battery monitoring, charging, predictive maintenance
   - 15 user stories

2️⃣ **Fleet Operations & Tracking** (75 pts, High Priority)
   - Real-time GPS, route optimization, dispatch
   - 20 user stories

3️⃣ **Driver Mobile Application** (40 pts, High Priority)
   - Navigation, delivery confirmation, communication
   - 12 user stories

4️⃣ **Analytics & Reporting** (65 pts, Medium Priority)
   - KPIs, cost analysis, environmental impact
   - 18 user stories

**📅 Sprint Plan:**
- Duration: 16 weeks (4 months)
- Team Velocity: 30 points/sprint
- Deliverables: MVP after Sprint 6, Full release after Sprint 8

**🔗 Ready to export to Jira!**

What's next?
1. Review and refine the backlog
2. Export to Jira
3. Move to Phase 3 (Architecture)
4. Adjust story points

Check the sidebar for all details! 👉""",
                "confidence_score": 94,
                "action": "content_generated",
                "artifacts": {
                    "epics": epics,
                    "sprint_plan": sprint_plan,
                    "type": "product_backlog"
                },
                "suggested_actions": [
                    "Review backlog",
                    "Export to Jira",
                    "Move to Phase 3",
                    "Refine estimates"
                ]
            }
        
        return {
            "response": "Let me help you create a product backlog! Tell me about the key features...",
            "confidence_score": 70,
            "action": "await_user_input"
        }
    
    def _generate_architecture(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Phase 3 content - Architecture"""
        
        if 'truck' in context.get('description', '').lower():
            architecture = {
                "system_architecture": """# System Architecture - Zero-Emission Trucking Platform

## High-Level Architecture

### Microservices Architecture
1. **Vehicle Management Service**
   - Battery monitoring
   - Charging management
   - Predictive maintenance
   - Vehicle telemetry

2. **Fleet Operations Service**
   - Real-time tracking
   - Route optimization
   - Dispatch management
   - Load management

3. **Driver Service**
   - Driver management
   - Mobile app backend
   - Communication
   - Schedule management

4. **Analytics Service**
   - Data aggregation
   - KPI calculation
   - Reporting
   - Predictive analytics

5. **Integration Service**
   - Third-party APIs
   - IoT device connectivity
   - External system integration

### Technology Stack
**Backend:**
- Language: Python (FastAPI) / Node.js
- Database: PostgreSQL (operational), TimescaleDB (telemetry)
- Cache: Redis
- Message Queue: RabbitMQ / Apache Kafka
- API Gateway: Kong / AWS API Gateway

**Frontend:**
- Web: React + TypeScript
- Mobile: React Native
- State Management: Redux
- UI Framework: Tailwind CSS

**Infrastructure:**
- Cloud: AWS (primary)
- Containers: Docker + Kubernetes
- CI/CD: GitHub Actions
- Monitoring: Datadog / New Relic

**IoT & Real-time:**
- MQTT for vehicle telemetry
- WebSocket for real-time updates
- AWS IoT Core for device management""",
                "infrastructure": """# Infrastructure Design

## Environment Structure

### Development
- EC2: t3.medium (4 instances)
- RDS: db.t3.medium (PostgreSQL)
- ElastiCache: cache.t3.micro
- Cost: ~$500/month

### QA/Staging
- ECS: Fargate (8 tasks)
- RDS: db.r5.large (Multi-AZ)
- ElastiCache: cache.r5.large
- Cost: ~$1,500/month

### Production
- EKS: 3 node cluster (m5.xlarge)
- RDS: db.r5.2xlarge (Multi-AZ + Read Replicas)
- ElastiCache: cache.r5.xlarge (Cluster mode)
- S3: Standard + Glacier
- CloudFront: CDN
- ALB: Application Load Balancer
- Cost: ~$5,000/month

## Scalability
- Auto-scaling: 5-50 pods
- Database: Read replicas for scaling
- Caching: Multi-layer (Application + CDN)
- CDN: CloudFront for global distribution""",
                "security": """# Security Architecture

## Authentication & Authorization
- OAuth 2.0 + JWT tokens
- Multi-factor authentication (MFA)
- Role-based access control (RBAC)
- API key management

## Data Security
- Encryption at rest: AES-256
- Encryption in transit: TLS 1.3
- Database encryption: AWS RDS encryption
- Secrets management: AWS Secrets Manager

## Network Security
- VPC with private subnets
- Security groups & NACLs
- WAF (Web Application Firewall)
- DDoS protection (AWS Shield)

## Compliance
- SOC 2 Type II
- GDPR compliance
- DOT regulations
- EPA requirements"""
            }
            
            return {
                "response": """✅ I've designed a comprehensive Architecture for your Trucking Platform!

**🏗️ System Architecture:**
- **Microservices Architecture** with 5 core services
- Vehicle Management, Fleet Operations, Driver, Analytics, Integration
- Event-driven communication

**💻 Technology Stack:**
- Backend: Python (FastAPI) + PostgreSQL + Redis
- Frontend: React + TypeScript + React Native
- Infrastructure: AWS + Kubernetes + Docker
- Real-time: MQTT + WebSocket for vehicle telemetry

**☁️ Infrastructure:**
- **Dev**: ~$500/month
- **QA**: ~$1,500/month
- **Production**: ~$5,000/month
- Auto-scaling: 5-50 pods
- Multi-AZ deployment

**🔐 Security:**
- OAuth 2.0 + JWT
- AES-256 encryption
- TLS 1.3
- SOC 2 + GDPR compliant

**What's next?**
1. Review architecture diagrams
2. Adjust tech stack if needed
3. Move to Phase 4 (Detailed Design)
4. Setup infrastructure

All architecture docs are in the sidebar! 👉""",
                "confidence_score": 93,
                "action": "content_generated",
                "artifacts": architecture,
                "suggested_actions": [
                    "Review architecture",
                    "Adjust tech stack",
                    "Move to Phase 4",
                    "Setup AWS account"
                ]
            }
        
        return {
            "response": "Let me design the architecture! What tech stack do you prefer?",
            "confidence_score": 70,
            "action": "await_user_input"
        }
    
    def _generate_detailed_design(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Phase 4 content - Detailed Design"""
        return {
            "response": "Phase 4: Detailed Design generation...",
            "confidence_score": 85
        }
    
    def _generate_code_tests(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Phase 5 content - Code & Tests"""
        return {
            "response": "Phase 5: Code and test generation...",
            "confidence_score": 85
        }
    
    def _generate_deployment_plan(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Phase 6 content - Deployment"""
        return {
            "response": "Phase 6: Deployment plan generation...",
            "confidence_score": 85
        }
    
    def _guide_approval_process(self, phase_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Guide through approval process"""
        return {
            "response": f"""📋 Let's set up approvals for Phase {phase_id}!

Based on this phase, you need approvals from:
{self._get_approvers_for_phase(phase_id)}

Would you like me to:
1. Create approval requests
2. Send notifications to stakeholders
3. Track approval status
4. Set up reminder workflows""",
            "confidence_score": 88,
            "action": "await_user_input"
        }
    
    def _suggest_next_steps(self, phase_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest next steps"""
        next_phase = phase_id + 1
        
        if phase_id < 6:
            return {
                "response": f"""🎯 Great progress! Here's what's next:

**Current Phase {phase_id} Status:**
- ✅ Content generated
- ⏳ Awaiting approvals

**Next Steps:**
1. Review generated content
2. Get stakeholder approvals
3. Move to Phase {next_phase}

**Phase {next_phase} Preview:**
{self.current_phase_prompts[next_phase]['name']}
{self.current_phase_prompts[next_phase]['description']}

Ready to proceed? Just say "Let's move to Phase {next_phase}"!""",
                "confidence_score": 90,
                "action": "guide_next_phase"
            }
        else:
            return {
                "response": """🎉 Congratulations! You've completed all 6 phases!

Your project is ready for production. Here's what you've accomplished:
✅ Phase 1: Requirements & Analysis
✅ Phase 2: Planning & Backlog
✅ Phase 3: Architecture
✅ Phase 4: Detailed Design
✅ Phase 5: Development & Testing
✅ Phase 6: Deployment & Operations

What would you like to do now?
- Review final deliverables
- Generate project summary
- Export all documentation
- Start project retrospective""",
                "confidence_score": 95,
                "action": "project_complete"
            }
    
    def _provide_contextual_help(self, query: str, phase_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide contextual help"""
        return {
            "response": f"""💡 I'm here to help with Phase {phase_id}!

**Current Phase:** {self.current_phase_prompts[phase_id]['name']}

**I can help you:**
- Generate phase content
- Review deliverables
- Setup approvals
- Answer questions
- Suggest next steps

What would you like me to help you with?""",
            "confidence_score": 80,
            "action": "await_user_input"
        }
    
    def _get_approvers_for_phase(self, phase_id: int) -> str:
        approvers_map = {
            1: "- Product Owner\n- BR Owner\n- Business Stakeholders",
            2: "- Project Manager\n- Product Owner\n- Technical Lead",
            3: "- Solution Architect\n- Technical Architect\n- Security Architect",
            4: "- Technical Lead\n- Backend Architect\n- Frontend Architect\n- UX Designer",
            5: "- Technical Lead\n- Senior Developer\n- QA Lead\n- Security Team",
            6: "- DevOps Lead\n- Technical Lead\n- Product Owner"
        }
        return approvers_map.get(phase_id, "- Project stakeholders")
    
    def _format_list(self, items: List[str]) -> str:
        """Format list items with bullets"""
        return "\n".join([f"  • {item}" for item in items])
    
    def _get_phase1_prompts(self) -> Dict[str, Any]:
        return {
            "name": "Phase 1: Requirements & Business Analysis",
            "description": "Define what needs to be built",
            "key_activities": [
                "Requirements collection",
                "PRD & BRD creation",
                "Risk assessment",
                "Feasibility analysis"
            ],
            "deliverables": ["PRD", "BRD", "Risk Assessment"],
            "ai_assistance": [
                "Extract requirements from conversations",
                "Generate PRD/BRD templates",
                "Identify risks automatically",
                "Suggest missing requirements"
            ]
        }
    
    def _get_phase2_prompts(self) -> Dict[str, Any]:
        return {
            "name": "Phase 2: Planning & Product Backlog",
            "description": "Plan effort and create backlog",
            "key_activities": [
                "Effort estimation",
                "Epic creation",
                "User story breakdown",
                "Sprint planning"
            ],
            "deliverables": ["Product Backlog", "Sprint Plan", "Release Roadmap"],
            "ai_assistance": [
                "Auto-generate epics from requirements",
                "Create user stories",
                "Estimate story points",
                "Optimize sprint distribution"
            ]
        }
    
    def _get_phase3_prompts(self) -> Dict[str, Any]:
        return {
            "name": "Phase 3: Architecture & High-Level Design",
            "description": "Design the overall system",
            "key_activities": [
                "System architecture",
                "Technology stack selection",
                "Infrastructure design",
                "Security architecture"
            ],
            "deliverables": ["Architecture Document", "Infrastructure Blueprint", "Security Plan"],
            "ai_assistance": [
                "Suggest architecture patterns",
                "Recommend tech stack",
                "Generate architecture diagrams",
                "Security best practices"
            ]
        }
    
    def _get_phase4_prompts(self) -> Dict[str, Any]:
        return {
            "name": "Phase 4: Detailed Design & Specifications",
            "description": "Create detailed specifications",
            "key_activities": [
                "Database design",
                "API specifications",
                "UX/UI design",
                "FSD creation"
            ],
            "deliverables": ["DB Schema", "API Specs", "FSD", "UX/UI Designs"],
            "ai_assistance": [
                "Generate database schemas",
                "Create API documentation",
                "Design wireframes",
                "Generate FSD"
            ]
        }
    
    def _get_phase5_prompts(self) -> Dict[str, Any]:
        return {
            "name": "Phase 5: Development, Testing & Code Review",
            "description": "Build and test the software",
            "key_activities": [
                "Backend development",
                "Frontend development",
                "Unit testing",
                "Integration testing",
                "QA"
            ],
            "deliverables": ["Working Software", "Test Reports", "Code Coverage"],
            "ai_assistance": [
                "Generate boilerplate code",
                "Auto-complete code",
                "Generate unit tests",
                "Code review suggestions"
            ]
        }
    
    def _get_phase6_prompts(self) -> Dict[str, Any]:
        return {
            "name": "Phase 6: Deployment, Release & Operations",
            "description": "Release to production and monitor",
            "key_activities": [
                "Staging deployment",
                "Production deployment",
                "Monitoring setup",
                "Documentation"
            ],
            "deliverables": ["Deployed Application", "Monitoring Dashboard", "Documentation"],
            "ai_assistance": [
                "Generate deployment checklist",
                "Create monitoring dashboards",
                "Generate documentation",
                "Suggest optimizations"
            ]
        }

