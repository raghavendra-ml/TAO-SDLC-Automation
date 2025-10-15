"""
RAG-based Chat Service with Multi-Node Architecture
Handles context-aware chat with Vector DB, SQL DB, and General AI fallback
"""
import os
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.enhanced_vector_store import EnhancedVectorStoreService
from app import models
import openai
from dotenv import load_dotenv
import json

load_dotenv()

class RAGChatService:
    """
    Multi-node RAG chat service with intelligent routing
    - Vector DB for semantic search
    - SQL DB for structured data
    - General AI for fallback
    """
    
    def __init__(self):
        try:
            self.vector_store = EnhancedVectorStoreService()
        except Exception as e:
            print(f"Warning: Vector store initialization failed: {e}")
            self.vector_store = None
        
        openai.api_key = os.getenv("OPENAI_API_KEY", "")
        self.use_real_ai = bool(openai.api_key and openai.api_key != "")
    
    async def process_chat_query(
        self,
        query: str,
        context_type: str,  # "dashboard" or "project"
        project_id: Optional[int] = None,
        phase_id: Optional[int] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Main entry point for chat queries with intelligent routing
        
        Args:
            query: User's question
            context_type: "dashboard" (global) or "project" (project-specific)
            project_id: Current project ID (if in project context)
            phase_id: Current phase ID (if in phase context)
            db: Database session
            
        Returns:
            AI response with sources and confidence
        """
        
        # Initialize conversation history if not provided
        if conversation_history is None:
            conversation_history = []
        
        # Step 1: Detect query intent (consider conversation history)
        intent = self._detect_query_intent(query, context_type, conversation_history)
        
        # Step 2: Route to appropriate node(s)
        if context_type == "dashboard":
            response = await self._handle_dashboard_query(query, intent, conversation_history, db)
        else:
            response = await self._handle_project_query(
                query, intent, project_id, phase_id, conversation_history, db
            )
        
        # Step 3: Store chat interaction in vector DB for future context
        if project_id and self.use_real_ai:
            self.vector_store.store_chat_embedding(
                project_id=project_id,
                phase_id=phase_id,
                chat_data={
                    "query": query,
                    "response": response["response"],
                    "intent": intent,
                    "sources": response.get("sources", [])
                },
                search_text=f"Q: {query}\nA: {response['response']}"
            )
        
        return response
    
    def _detect_query_intent(self, query: str, context_type: str, conversation_history: List[Dict[str, Any]] = None) -> str:
        """
        Detect what the user is asking about (considering conversation history)
        
        Returns:
            Intent category: "project_list", "project_status", "phase_guidance",
                           "requirement_info", "general_sdlc", "data_query"
        """
        query_lower = query.lower()
        
        # Check if query refers to previous context (e.g., "yes", "tell me more", "yes with phase 2")
        if conversation_history and len(conversation_history) > 0:
            # Check for simple affirmatives or follow-up phrases
            if any(word in query_lower for word in ["yes", "sure", "ok", "okay", "tell me more", "continue", "go ahead"]):
                # Continue from previous intent - extract from last AI response
                return "follow_up"
            
            # Check if asking about specific phase as follow-up (e.g., "phase 2", "with phase 2")
            if any(word in query_lower for word in ["phase 2", "phase 3", "phase 4", "phase 5", "phase 6"]) and len(query_lower.split()) <= 5:
                return "follow_up"
        
        # Dashboard context intents
        if context_type == "dashboard":
            if any(word in query_lower for word in ["approval", "pending", "waiting", "need to approve", "approvals are pending"]):
                return "approval_query"
            elif any(word in query_lower for word in ["how many", "count", "list", "all projects"]):
                return "project_list"
            elif any(word in query_lower for word in ["status", "progress"]) and "phase" not in query_lower:
                return "project_status"
            elif any(word in query_lower for word in ["create", "start", "new project", "how do i create"]):
                return "project_creation"
            else:
                return "dashboard_general"
        
        # Project context intents
        else:
            if any(word in query_lower for word in ["next step", "what should", "how to", "guide"]):
                return "phase_guidance"
            elif any(word in query_lower for word in ["requirement", "feature", "user story"]):
                return "requirement_info"
            elif any(word in query_lower for word in ["risk", "issue", "problem"]):
                return "risk_analysis"
            elif any(word in query_lower for word in ["stakeholder", "approval", "who"]):
                return "stakeholder_info"
            elif any(word in query_lower for word in ["status", "progress", "complete"]):
                return "project_status"
            else:
                return "project_general"
    
    async def _handle_dashboard_query(
        self,
        query: str,
        intent: str,
        conversation_history: List[Dict[str, Any]],
        db: Session
    ) -> Dict[str, Any]:
        """Handle queries in dashboard context (global view)"""
        
        # Node 1: SQL DB - Get structured data
        sql_context = self._get_dashboard_sql_context(db)
        
        # Node 2: Vector DB - Semantic search across all projects (dashboard context)
        vector_context = []
        if self.vector_store:
            try:
                vector_results = self.vector_store.search_dashboard_context(
                    query_text=query,
                    limit=5
                )
                vector_context = [r["content"] for r in vector_results]
            except Exception as e:
                print(f"Vector search error: {e}")
        
        # Node 3: Generate response with context
        if intent == "approval_query":
            response = self._generate_approval_response(sql_context, query)
        elif intent == "project_list":
            response = self._generate_project_list_response(sql_context, query)
        elif intent == "project_status":
            response = self._generate_project_status_response(sql_context, query)
        elif intent == "project_creation":
            response = self._generate_project_creation_guidance()
        elif intent == "follow_up":
            response = self._handle_follow_up(query, conversation_history, sql_context, db)
        else:
            response = self._generate_dashboard_general_response(
                query, sql_context, vector_context
            )
        
        return response
    
    async def _handle_project_query(
        self,
        query: str,
        intent: str,
        project_id: int,
        phase_id: Optional[int],
        conversation_history: List[Dict[str, Any]],
        db: Session
    ) -> Dict[str, Any]:
        """Handle queries in project context (project-specific)"""
        
        # Node 1: SQL DB - Get project data
        sql_context = self._get_project_sql_context(project_id, phase_id, db)
        
        # Node 2: Vector DB - Semantic search in project context
        vector_context = []
        if self.vector_store:
            try:
                vector_results = self.vector_store.search_project_context(
                    project_id=project_id,
                    query_text=query,
                    phase_id=phase_id,
                    limit=5
                )
                vector_context = [r["content"] for r in vector_results]
            except Exception as e:
                print(f"Vector search error: {e}")
        
        # Node 3: Generate context-aware response
        if intent == "phase_guidance":
            response = self._generate_phase_guidance(sql_context, phase_id)
        elif intent == "requirement_info":
            response = self._generate_requirement_info(sql_context, vector_context, query)
        elif intent == "risk_analysis":
            response = self._generate_risk_analysis(sql_context, vector_context)
        elif intent == "stakeholder_info":
            response = self._generate_stakeholder_info(sql_context)
        elif intent == "project_status":
            response = self._generate_project_progress(sql_context)
        else:
            response = self._generate_project_general_response(
                query, sql_context, vector_context
            )
        
        return response
    
    def _get_dashboard_sql_context(self, db: Session) -> Dict[str, Any]:
        """Get structured data from SQL DB for dashboard context"""
        try:
            # Get all projects with their phases
            projects = db.query(models.Project).all()
            
            context = {
                "total_projects": len(projects),
                "projects": []
            }
            
            for project in projects:
                phases = db.query(models.Phase).filter(
                    models.Phase.project_id == project.id
                ).all()
                
                context["projects"].append({
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "status": project.status,
                    "total_phases": len(phases),
                    "completed_phases": len([p for p in phases if p.status == "completed"]),
                    "current_phase": next((p.phase_name for p in phases if p.status == "in_progress"), None)
                })
            
            # Get overall statistics
            # Count phases with pending_approval status (not Approval records)
            pending_approval_count = db.query(models.Phase).filter(
                models.Phase.status == "pending_approval"
            ).count()
            
            context["statistics"] = {
                "active_projects": len([p for p in projects if p.status == "active"]),
                "completed_projects": len([p for p in projects if p.status == "completed"]),
                "pending_approvals": pending_approval_count
            }
            
            return context
        except Exception as e:
            return {"error": str(e), "total_projects": 0, "projects": []}
    
    def _get_project_sql_context(
        self,
        project_id: int,
        phase_id: Optional[int],
        db: Session
    ) -> Dict[str, Any]:
        """Get structured data from SQL DB for project context"""
        try:
            project = db.query(models.Project).filter(
                models.Project.id == project_id
            ).first()
            
            if not project:
                return {"error": "Project not found"}
            
            phases = db.query(models.Phase).filter(
                models.Phase.project_id == project_id
            ).order_by(models.Phase.phase_number).all()
            
            current_phase = None
            if phase_id:
                current_phase = db.query(models.Phase).filter(
                    models.Phase.id == phase_id
                ).first()
            
            context = {
                "project": {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "status": project.status,
                    "created_at": str(project.created_at)
                },
                "phases": [
                    {
                        "id": p.id,
                        "number": p.phase_number,
                        "name": p.phase_name,
                        "status": p.status,
                        "data": p.data or {}
                    }
                    for p in phases
                ],
                "current_phase": {
                    "id": current_phase.id,
                    "number": current_phase.phase_number,
                    "name": current_phase.phase_name,
                    "status": current_phase.status,
                    "data": current_phase.data or {}
                } if current_phase else None,
                "progress": {
                    "total_phases": len(phases),
                    "completed": len([p for p in phases if p.status == "completed"]),
                    "in_progress": len([p for p in phases if p.status == "in_progress"]),
                    "pending": len([p for p in phases if p.status == "pending"])
                }
            }
            
            return context
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_project_list_response(
        self,
        sql_context: Dict[str, Any],
        query: str
    ) -> Dict[str, Any]:
        """Generate response for project list queries"""
        total = sql_context.get("total_projects", 0)
        projects = sql_context.get("projects", [])
        
        if "phase" in query.lower() and "requirements" in query.lower():
            # Filter projects in Requirements phase
            req_projects = [
                p for p in projects 
                if p.get("current_phase") and "Requirements" in p["current_phase"]
            ]
            count = len(req_projects)
            response = f"There are **{count} projects** currently in the 'Requirements & Business Analysis' phase:\n\n"
            for p in req_projects:
                response += f"- **{p['name']}**: {p.get('description', 'No description')}\n"
        else:
            response = f"You have **{total} total projects** in your SDLC platform:\n\n"
            for p in projects[:5]:  # Show first 5
                status_emoji = "🟢" if p["status"] == "active" else "🔵" if p["status"] == "completed" else "⚪"
                response += f"{status_emoji} **{p['name']}** - {p['completed_phases']}/{p['total_phases']} phases completed\n"
            
            if total > 5:
                response += f"\n... and {total - 5} more projects."
        
        return {
            "response": response,
            "confidence_score": 95,
            "sources": ["SQL Database"],
            "context_type": "dashboard"
        }
    
    def _generate_project_status_response(
        self,
        sql_context: Dict[str, Any],
        query: str
    ) -> Dict[str, Any]:
        """Generate response for project status queries"""
        stats = sql_context.get("statistics", {})
        
        response = f"""📊 **Project Status Overview**

**Active Projects**: {stats.get('active_projects', 0)}
**Completed Projects**: {stats.get('completed_projects', 0)}
**Pending Approvals**: {stats.get('pending_approvals', 0)}

Your projects are progressing well! """
        
        if stats.get('pending_approvals', 0) > 0:
            response += f"You have {stats['pending_approvals']} approvals waiting for review."
        
        return {
            "response": response,
            "confidence_score": 90,
            "sources": ["SQL Database"],
            "context_type": "dashboard"
        }
    
    def _generate_project_creation_guidance(self) -> Dict[str, Any]:
        """Generate guidance for creating a new project"""
        response = """🚀 **Creating a New Project**

To create a new project, follow these steps:

1. Click the **"+ New Project"** button in the top right
2. Fill in the project details:
   - Project Name
   - Description
   - Select team members
3. Click **"Create Project"**

The system will automatically:
- Create all 6 SDLC phases
- Set up approval workflows
- Initialize AI assistance

**The 6 phases are**:
1. Requirements & Business Analysis
2. Planning & Product Backlog
3. Architecture & High-Level Design
4. Detailed Design & Specification
5. Development, Testing & Code Review
6. Deployment, Release & Operations

Would you like me to guide you through any specific phase?"""
        
        return {
            "response": response,
            "confidence_score": 100,
            "sources": ["SDLC Knowledge Base"],
            "context_type": "dashboard"
        }
    
    def _generate_approval_response(
        self,
        sql_context: Dict[str, Any],
        query: str
    ) -> Dict[str, Any]:
        """Generate response for approval queries"""
        stats = sql_context.get("statistics", {})
        pending = stats.get("pending_approvals", 0)
        projects = sql_context.get("projects", [])
        
        if pending == 0:
            response = """✅ **No Pending Approvals**

Great news! You don't have any approvals waiting for your review at the moment.

All project phases are either in progress or already approved."""
        else:
            response = f"""📋 **Pending Approvals**

You have **{pending} approval{'s' if pending != 1 else ''}** waiting for your review.

"""
            # Add details about which projects have pending approvals
            response += "**Pending submissions:**\n"
            for project in projects:
                project_name = project.get("name", "Unknown Project")
                response += f"- {project_name}\n"
            
            response += """
**To review and approve:**
1. Click on **"Approval Center"** in the sidebar
2. Review the phase submissions
3. Click **"Approve"** or **"Reject"** with comments

**What you can review:**
- Requirements & Business Analysis (Phase 1)
- Planning & Product Backlog (Phase 2)
- Architecture & High-Level Design (Phase 3)
- And other phase submissions

Would you like me to help you navigate to the Approval Center?"""
        
        return {
            "response": response,
            "confidence_score": 95,
            "sources": ["SQL Database"],
            "context_type": "dashboard"
        }
    
    def _handle_follow_up(
        self,
        query: str,
        conversation_history: List[Dict[str, Any]],
        sql_context: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Handle follow-up queries based on conversation context"""
        query_lower = query.lower()
        
        # Check what was asked before
        if len(conversation_history) >= 2:
            last_user_query = ""
            for msg in reversed(conversation_history):
                if msg.get("role") == "user":
                    last_user_query = msg.get("content", "").lower()
                    break
            
            # If previous question was about creating a project and now asking about phase 2
            if "create" in last_user_query or "new project" in last_user_query:
                if "phase 2" in query_lower or "planning" in query_lower or "backlog" in query_lower:
                    return {
                        "response": """📊 **Phase 2: Planning & Product Backlog**

After creating your project, Phase 2 involves:

**Key Activities:**
1. **Generate Epics** - High-level business features
2. **Create User Stories** - Detailed requirements from user perspective
3. **Resource Planning** - Calculate team capacity and sprints
4. **Submit for Approval** - Send backlog for stakeholder review

**How to work in Phase 2:**
1. Go to your project page
2. Navigate to **"Phase 2: Planning & Product Backlog"**
3. Click **"Generate Epics"** button (AI will create them)
4. Click **"Generate User Stories"** for each epic
5. Review and edit as needed
6. Click **"Calculate Capacity"** for resource planning
7. Click **"Submit Phase 2 for Approval"**

**AI Features:**
- Auto-generates epics from Phase 1 requirements
- Creates realistic user stories (2-10 per epic)
- Estimates story points and complexity
- Confidence scoring for quality assurance

Ready to start working on Phase 2?""",
                        "confidence_score": 95,
                        "sources": ["SDLC Knowledge Base", "Context"],
                        "context_type": "dashboard"
                    }
        
        # Default follow-up response
        return {
            "response": "I'd be happy to help! Could you please provide more details about what you'd like to know?",
            "confidence_score": 50,
            "sources": ["Context"],
            "context_type": "dashboard"
        }
    
    def _generate_phase_guidance(
        self,
        sql_context: Dict[str, Any],
        phase_id: Optional[int]
    ) -> Dict[str, Any]:
        """Generate guidance for current phase"""
        current_phase = sql_context.get("current_phase")
        
        if not current_phase:
            return {
                "response": "I need to know which phase you're in to provide guidance. Could you specify the phase?",
                "confidence_score": 50,
                "sources": [],
                "context_type": "project"
            }
        
        phase_name = current_phase["name"]
        phase_number = current_phase["number"]
        
        guidance = {
            1: """📋 **Phase 1: Requirements & Business Analysis**

**Next Steps**:
1. ✅ **Upload Documents**: Click "Upload Documents" to add requirement files (Excel, Word, Text)
2. ✅ **Extract with AI**: Convert documents to Gherkin format
3. ✅ **Review Requirements**: Expand each requirement to see scenarios
4. ✅ **Generate PRD**: Click "Generate with AI" in the PRD section
5. ✅ **Generate BRD**: Click "Generate with AI" in the BRD section
6. ✅ **Analyze Risks**: Use "Analyze Risks with AI"
7. ✅ **Add Stakeholders**: Select approvers from database
8. ✅ **Submit for Approval**: Once all documents are ready

**Tips**:
- Be detailed in requirements for better AI conversion
- Approve requirements before generating PRD/BRD
- Export requirements as .feature files for testing""",
            
            2: """📊 **Phase 2: Planning & Product Backlog**

**Next Steps**:
1. Convert requirements to Epics
2. Break down Epics into User Stories
3. Estimate story points
4. Prioritize backlog
5. Plan sprints
6. Submit for approval

**Tips**:
- Use AI to generate user stories from requirements
- Follow INVEST criteria for user stories
- Consider dependencies between stories""",
            
            3: """🏗️ **Phase 3: Architecture & High-Level Design**

**Next Steps**:
1. Define system architecture
2. Create component diagrams
3. Design data flow
4. Plan infrastructure
5. Document technical decisions
6. Submit for approval

**Tips**:
- Consider scalability and performance
- Document architectural decisions (ADRs)
- Review with technical leads""",
            
            4: """📐 **Phase 4: Detailed Design & Specification**

**Next Steps**:
1. Create detailed component designs
2. Design database schema
3. Define API contracts
4. Write technical specifications
5. Create sequence diagrams
6. Submit for approval

**Tips**:
- Be specific about interfaces
- Document edge cases
- Include error handling""",
            
            5: """💻 **Phase 5: Development, Testing & Code Review**

**Next Steps**:
1. Implement features
2. Write unit tests
3. Conduct code reviews
4. Run integration tests
5. Fix bugs and issues
6. Submit for QA approval

**Tips**:
- Follow coding standards
- Write tests first (TDD)
- Review code thoroughly""",
            
            6: """🚀 **Phase 6: Deployment, Release & Operations**

**Next Steps**:
1. Prepare deployment plan
2. Set up CI/CD pipeline
3. Deploy to staging
4. Run smoke tests
5. Deploy to production
6. Monitor and support

**Tips**:
- Have rollback plan ready
- Monitor metrics closely
- Document deployment process"""
        }
        
        response = guidance.get(phase_number, "Phase guidance not available.")
        
        return {
            "response": response,
            "confidence_score": 95,
            "sources": ["SDLC Knowledge Base", "Project Data"],
            "context_type": "project"
        }
    
    def _generate_requirement_info(
        self,
        sql_context: Dict[str, Any],
        vector_context: List[str],
        query: str
    ) -> Dict[str, Any]:
        """Generate response about requirements using vector search"""
        
        if vector_context:
            response = "Based on your project requirements:\n\n"
            for i, context in enumerate(vector_context[:3], 1):
                response += f"{i}. {context[:200]}...\n\n"
            response += "\nWould you like more details about any specific requirement?"
        else:
            response = """I don't have specific requirement information yet. 

To add requirements:
1. Go to Phase 1: Requirements & Business Analysis
2. Upload requirement documents or add manually
3. Use "Extract with AI" to convert to Gherkin format

Once requirements are added, I'll be able to search and answer questions about them!"""
        
        return {
            "response": response,
            "confidence_score": 85 if vector_context else 70,
            "sources": ["Vector Database", "Project Data"] if vector_context else ["SDLC Knowledge"],
            "context_type": "project"
        }
    
    def _generate_risk_analysis(
        self,
        sql_context: Dict[str, Any],
        vector_context: List[str]
    ) -> Dict[str, Any]:
        """Generate risk analysis response"""
        current_phase = sql_context.get("current_phase", {})
        phase_data = current_phase.get("data", {})
        risks = phase_data.get("risks", [])
        
        if risks:
            response = "🚨 **Identified Risks**:\n\n"
            for risk in risks[:5]:
                severity = risk.get("severity", "Medium")
                emoji = "🔴" if severity == "High" else "🟡" if severity == "Medium" else "🟢"
                response += f"{emoji} **{risk.get('risk', 'Unknown risk')}**\n"
                response += f"   - Severity: {severity}\n"
                response += f"   - Mitigation: {risk.get('mitigation', 'TBD')}\n\n"
        else:
            response = """No risks have been identified yet.

To analyze risks:
1. Go to Phase 1: Requirements & Business Analysis
2. Click "Analyze Risks with AI"
3. Review and approve identified risks

AI will analyze your requirements and suggest potential risks and mitigation strategies."""
        
        return {
            "response": response,
            "confidence_score": 90 if risks else 75,
            "sources": ["Project Data", "Risk Analysis"],
            "context_type": "project"
        }
    
    def _generate_stakeholder_info(self, sql_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate stakeholder information"""
        current_phase = sql_context.get("current_phase", {})
        phase_data = current_phase.get("data", {})
        stakeholders = phase_data.get("stakeholders", [])
        
        if stakeholders:
            response = "👥 **Project Stakeholders**:\n\n"
            for sh in stakeholders:
                status_emoji = "✅" if sh.get("status") == "approved" else "⏳"
                response += f"{status_emoji} **{sh.get('role', 'Unknown')}**: {sh.get('name', 'Unknown')}\n"
        else:
            response = """No stakeholders have been added yet.

To add stakeholders:
1. Go to Phase 1: Requirements & Business Analysis
2. Click "Select from Database" or "Add Custom Stakeholder"
3. Choose approvers for this phase

Stakeholders will be notified when you submit for approval."""
        
        return {
            "response": response,
            "confidence_score": 95 if stakeholders else 80,
            "sources": ["Project Data"],
            "context_type": "project"
        }
    
    def _generate_project_progress(self, sql_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project progress response"""
        progress = sql_context.get("progress", {})
        project = sql_context.get("project", {})
        
        total = progress.get("total_phases", 6)
        completed = progress.get("completed", 0)
        in_progress = progress.get("in_progress", 0)
        
        percentage = int((completed / total) * 100) if total > 0 else 0
        
        response = f"""📊 **Project Progress: {project.get('name', 'Unknown')}**

**Overall Progress**: {percentage}% ({completed}/{total} phases completed)

**Phase Status**:
- ✅ Completed: {completed}
- 🔄 In Progress: {in_progress}
- ⏳ Pending: {progress.get('pending', 0)}

"""
        
        if percentage < 30:
            response += "🚀 You're just getting started! Focus on completing Phase 1 first."
        elif percentage < 70:
            response += "💪 Good progress! Keep the momentum going."
        else:
            response += "🎉 Almost there! You're in the final stretch."
        
        return {
            "response": response,
            "confidence_score": 95,
            "sources": ["Project Data"],
            "context_type": "project"
        }
    
    def _generate_dashboard_general_response(
        self,
        query: str,
        sql_context: Dict[str, Any],
        vector_context: List[str]
    ) -> Dict[str, Any]:
        """Generate general response for dashboard queries"""
        
        # Fallback to general SDLC knowledge
        response = """I'm here to help you manage your SDLC projects! 

**I can help you with**:
- 📊 Project status and progress
- 📋 Creating new projects
- ✅ Checking approvals
- 📈 Viewing statistics

**Try asking**:
- "How many projects are there?"
- "Show me active projects"
- "How do I create a new project?"
- "What approvals are pending?"

Or click on a project to get project-specific guidance!"""
        
        return {
            "response": response,
            "confidence_score": 70,
            "sources": ["General AI"],
            "context_type": "dashboard"
        }
    
    def _generate_project_general_response(
        self,
        query: str,
        sql_context: Dict[str, Any],
        vector_context: List[str]
    ) -> Dict[str, Any]:
        """Generate general response for project queries"""
        
        project_name = sql_context.get("project", {}).get("name", "this project")
        
        response = f"""I'm here to help you with **{project_name}**!

**I can help you with**:
- 🎯 Phase guidance and next steps
- 📋 Requirements and features
- 🚨 Risk analysis
- 👥 Stakeholder information
- 📊 Project progress

**Try asking**:
- "What should I do next?"
- "Show me the requirements"
- "What are the risks?"
- "Who are the stakeholders?"
- "What's the project status?"

I'm learning about your project as you add more information!"""
        
        return {
            "response": response,
            "confidence_score": 75,
            "sources": ["General AI", "Project Context"],
            "context_type": "project"
        }
