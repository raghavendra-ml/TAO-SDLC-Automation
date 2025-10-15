"""
RAG (Retrieval Augmented Generation) AI Service
Uses vector store for context-aware responses
"""
from typing import Dict, Any, List, Optional
from app.services.vector_store import get_vector_store
import os

class RAGAIService:
    """AI Service with RAG capabilities using vector store"""
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.api_key = os.getenv("OPENAI_API_KEY", "")
    
    async def chat_with_context(
        self,
        user_query: str,
        project_id: int,
        phase_id: Optional[int] = None,
        phase_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user query with project context from vector store
        """
        # Get relevant context from vector store
        context = self.vector_store.get_relevant_context(
            query=user_query,
            project_id=project_id,
            phase_id=phase_id,
            max_tokens=2000
        )
        
        # Build enhanced prompt with context
        system_prompt = f"""You are an AI assistant for an SDLC platform. 
You have access to the project's history, requirements, documents, and previous conversations.

Current Phase: {phase_name or 'Not specified'}
Project ID: {project_id}

RELEVANT PROJECT CONTEXT:
{context}

Use the above context to provide accurate, context-aware responses.
If the context contains relevant information, reference it in your answer.
If you don't find relevant context, provide general SDLC guidance.
"""
        
        # Generate response (mock for now, will use OpenAI in production)
        response_text = self._generate_response(system_prompt, user_query, context)
        
        # Store this interaction in vector store for future context
        self.vector_store.store_chat_message(
            project_id=project_id,
            phase_id=phase_id,
            user_message=user_query,
            ai_response=response_text,
            metadata={'phase_name': phase_name}
        )
        
        return {
            "response": response_text,
            "confidence_score": 85,
            "context_used": bool(context),
            "sources": self._extract_sources(context)
        }
    
    def _generate_response(
        self,
        system_prompt: str,
        user_query: str,
        context: str
    ) -> str:
        """Generate AI response (mock implementation)"""
        
        # Analyze query intent
        query_lower = user_query.lower()
        
        # Context-aware responses
        if context and len(context) > 100:
            if 'requirement' in query_lower:
                return f"""Based on your project's requirements, I can see you have several documented features.

Here's what I found relevant to your question:

{self._summarize_context(context, max_lines=5)}

Would you like me to:
1. Provide more details about any specific requirement?
2. Generate additional scenarios?
3. Convert these to user stories for Phase 2?

Let me know how I can help!"""
            
            elif 'epic' in query_lower or 'user stor' in query_lower:
                return f"""I can help you create epics and user stories based on your project's requirements!

From your project context:
{self._summarize_context(context, max_lines=3)}

I can:
1. Group related features into epics
2. Break down each epic into user stories
3. Add acceptance criteria
4. Estimate story points

Shall we start with creating epics?"""
            
            elif 'generate' in query_lower or 'create' in query_lower:
                return f"""I found relevant context from your project:

{self._summarize_context(context, max_lines=4)}

I can generate:
- Product Requirements Documents (PRD)
- Business Requirements Documents (BRD)
- Functional Specification Documents (FSD)
- Test Scenarios
- API Specifications

What would you like me to generate?"""
        
        # Default responses for common queries
        if 'start' in query_lower or 'begin' in query_lower:
            return self._get_phase_guidance(user_query)
        elif 'deliverable' in query_lower:
            return self._get_deliverables_info(user_query)
        elif 'best practice' in query_lower:
            return self._get_best_practices(user_query)
        elif 'help' in query_lower or 'how' in query_lower:
            return self._get_help_info(user_query)
        
        # Generic response
        return f"""I'm here to help with your SDLC process!

I can assist with:
• Requirements gathering and analysis
• Document generation (PRD, BRD, FSD)
• Epic and user story creation
• Architecture design guidance
• Test scenario generation
• Best practices and recommendations

Your question: "{user_query}"

Could you please provide more details about what you'd like help with?"""
    
    def _summarize_context(self, context: str, max_lines: int = 5) -> str:
        """Summarize context to key points"""
        lines = [line.strip() for line in context.split('\n') if line.strip() and not line.strip().startswith('[')]
        relevant_lines = [line for line in lines if len(line) > 20][:max_lines]
        return '\n• ' + '\n• '.join(relevant_lines) if relevant_lines else context[:500]
    
    def _extract_sources(self, context: str) -> List[str]:
        """Extract source types from context"""
        sources = []
        if '[REQUIREMENT' in context:
            sources.append('Requirements')
        if '[DOCUMENT' in context:
            sources.append('Documents')
        if '[CHAT' in context:
            sources.append('Previous Conversations')
        return sources
    
    def _get_phase_guidance(self, query: str) -> str:
        """Provide phase-specific guidance"""
        return """To start this phase effectively:

1. **Review Phase Objectives**
   - Understand what needs to be delivered
   - Review key activities and deliverables

2. **Gather Necessary Information**
   - Upload any existing documents
   - Add relevant stakeholders
   - Review previous phase outputs

3. **Use AI Tools**
   - Click "Generate with AI" for document templates
   - Upload requirements for automatic extraction
   - Ask me questions as you go

4. **Collaborate**
   - Add team members as stakeholders
   - Request approvals when ready
   - Track progress

Would you like specific guidance for any of these steps?"""
    
    def _get_deliverables_info(self, query: str) -> str:
        """Provide deliverables information"""
        return """Key deliverables for each phase:

**Phase 1: Requirements & Business Analysis**
✅ Product Requirements Document (PRD)
✅ Business Requirements Document (BRD)
✅ Risk Assessment Report
✅ Stakeholder Sign-offs

**Phase 2: Planning & Product Backlog**
✅ Product Backlog
✅ Epic Breakdown
✅ User Stories with Acceptance Criteria
✅ Sprint Planning

**Phase 3: Architecture & High-Level Design**
✅ System Architecture Diagram
✅ Infrastructure Blueprint
✅ Security Architecture Plan
✅ API Architecture

**Phase 4: Detailed Design & Specifications**
✅ Database Schema Design
✅ API Specifications
✅ Functional Specification Document (FSD)
✅ UX/UI Designs

**Phase 5: Development & Testing**
✅ Working Software
✅ Unit Tests
✅ Integration Tests
✅ Code Coverage Reports

**Phase 6: Deployment & Operations**
✅ Deployed Application
✅ Monitoring Dashboard
✅ Documentation
✅ Runbooks

Which phase would you like more details about?"""
    
    def _get_best_practices(self, query: str) -> str:
        """Provide best practices"""
        return """SDLC Best Practices:

🎯 **Planning**
- Start with clear, measurable objectives
- Involve all stakeholders early
- Use iterative approach

📋 **Requirements**
- Write testable requirements
- Use Gherkin format (Given/When/Then)
- Prioritize ruthlessly

🏗️ **Design**
- Follow SOLID principles
- Design for scalability
- Document decisions

💻 **Development**
- Write clean, maintainable code
- Test-driven development (TDD)
- Code reviews are mandatory

🧪 **Testing**
- Automate everything possible
- Test early and often
- Include security testing

🚀 **Deployment**
- Use CI/CD pipelines
- Blue-green deployments
- Monitor everything

Which area would you like specific guidance on?"""
    
    def _get_help_info(self, query: str) -> str:
        """Provide help information"""
        return """I'm your AI Copilot! Here's how I can help:

🤖 **Document Generation**
- "Generate a PRD for user authentication"
- "Create BRD for e-commerce platform"
- "Write FSD for API integration"

📊 **Requirements Processing**
- Upload Excel/Word/Text files
- I'll extract and convert to Gherkin format
- Generate test scenarios automatically

📝 **Content Creation**
- Generate user stories from requirements
- Create epics and backlog items
- Write acceptance criteria

💡 **Guidance & Advice**
- "What should I do in Phase 1?"
- "Best practices for API design"
- "How to write good requirements?"

🔍 **Project-Specific Help**
- I remember your project context
- Reference previous requirements
- Provide tailored suggestions

Just ask me anything! I'm here to help."""
    
    async def store_phase_completion(
        self,
        project_id: int,
        phase_id: int,
        phase_name: str,
        deliverables: Dict[str, Any]
    ):
        """Store phase completion data in vector store"""
        content = f"""Phase Completed: {phase_name}
        
Deliverables:
{self._format_deliverables(deliverables)}

Status: Complete
"""
        self.vector_store.store_document(
            project_id=project_id,
            phase_id=phase_id,
            document_type=f'phase_completion_{phase_id}',
            content=content,
            metadata={'phase_name': phase_name, 'deliverables': deliverables}
        )
    
    def _format_deliverables(self, deliverables: Dict[str, Any]) -> str:
        """Format deliverables for storage"""
        lines = []
        for key, value in deliverables.items():
            if isinstance(value, str):
                lines.append(f"- {key}: {value[:200]}")
            else:
                lines.append(f"- {key}: {str(value)[:200]}")
        return '\n'.join(lines)

