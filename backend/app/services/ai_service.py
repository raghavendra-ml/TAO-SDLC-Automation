import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key)
        
    async def process_query(self, query: str, phase_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user query with AI assistance
        """
        # Mock response for now - integrate with actual LLM in production
        return {
            "response": f"AI response for '{query}' in phase '{phase_name}'. Context: {context}",
            "confidence_score": 85,
            "alternatives": [
                "Alternative approach 1",
                "Alternative approach 2"
            ],
            "explanation": "This is the recommended approach based on best practices."
        }
    
    async def generate_content(self, phase_name: str, content_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate phase-specific content
        """
        # Generate content based on phase and type
        if "Requirements" in phase_name:
            if content_type == "prd":
                content = await self._generate_prd(data)
            elif content_type == "brd":
                content = await self._generate_brd(data)
            elif content_type == "requirements":
                content = self._generate_requirements(data)
            else:
                content = "Generated content for " + content_type
        elif "Planning" in phase_name:
            if content_type == "epics":
                content = await self._generate_epics(data)
            elif content_type == "user_stories":
                content = await self._generate_user_stories(data)
            else:
                content = "Generated planning content"
        elif "Architecture" in phase_name:
            if content_type == "architecture":
                content = self._generate_architecture(data)
            else:
                content = "Generated architecture content"
        else:
            content = f"Generated {content_type} for {phase_name}"
        
        return {
            "content": content,
            "confidence_score": 85
        }
    
    async def _generate_prd(self, data: Dict[str, Any]) -> str:
        """
        Generate Product Requirements Document using OpenAI based on collected requirements.
        Uses proper template structure and dynamically fills with analyzed requirement data.
        """
        # Extract requirements from data
        requirements = data.get('requirements', [])
        gherkin_reqs = data.get('gherkinRequirements', [])
        project_info = data.get('project', {})
        
        print(f"[INFO] Generating PRD using OpenAI for project: {project_info.get('name', 'Project')}")
        
        # Prepare requirements summary for OpenAI
        req_summary = ""
        all_reqs = gherkin_reqs or requirements
        
        for idx, req in enumerate(all_reqs, 1):
            if isinstance(req, dict):
                req_summary += f"\n{idx}. **{req.get('feature', req.get('title', 'Requirement'))}**\n"
                if 'as_a' in req:
                    req_summary += f"   - User Story: As a {req.get('as_a')}, I want {req.get('i_want')}, so that {req.get('so_that')}\n"
                    req_summary += f"   - Priority: {req.get('priority', 'Medium')}\n"
                    req_summary += f"   - Status: {req.get('status', 'draft')}\n"
                    
                scenarios = req.get('scenarios', [])
                if scenarios:
                        req_summary += f"   - Scenarios ({len(scenarios)}):\n"
                        for scenario in scenarios[:2]:  # First 2 scenarios
                            req_summary += f"     * {scenario.get('title')}\n"
                            if scenario.get('given'):
                                req_summary += f"       - Given: {', '.join(scenario.get('given')[:2])}\n"
                            if scenario.get('when'):
                                req_summary += f"       - When: {', '.join(scenario.get('when')[:2])}\n"
                            if scenario.get('then'):
                                req_summary += f"       - Then: {', '.join(scenario.get('then')[:2])}\n"
        
        if not req_summary:
            # Fallback to basic PRD if no requirements
            print("[WARNING] No requirements found, generating basic PRD template")
            return f"""# Product Requirements Document (PRD)

## Project: {project_info.get('name', 'Project')}

**Note**: This is a template PRD. Please add requirements to Phase 1 and regenerate for a complete document.

## 1. Product Overview
{project_info.get('description', 'Product description to be added')}

## 2. Requirements
No requirements have been collected yet. Please complete Phase 1 (Requirements Gathering) first.

---
*Generated by TAO SDLC AI Copilot*"""
        
        # Create OpenAI prompt for intelligent PRD generation (optimized for speed)
        prompt = f"""Generate a professional Product Requirements Document (PRD) for this project.

**Project**: {project_info.get('name', 'Project')}
**Description**: {project_info.get('description', 'Software project')}

**Requirements**:
{req_summary}

**Include these sections with ACTUAL data from requirements**:
1. Executive Summary (2-3 paragraphs - purpose, objectives, value)
2. Product Overview (what's being built, target users)
3. User Personas (2-3 based on actual user roles in requirements)
4. Feature Requirements (for each: name, priority, user story, acceptance criteria - use ACTUAL data)
5. Functional Requirements (capabilities, rules, data needs)
6. Non-Functional Requirements (performance, security, scalability, usability)
7. UX/UI (key flows, principles)
8. Technical Considerations (stack, architecture, integrations)
9. Success Metrics & KPIs (specific, measurable)
10. Timeline & Milestones (phases, dependencies)
11. Risks & Mitigation
12. Assumptions & Constraints
13. Out of Scope

**Format**: Professional markdown, clear headings, bullet lists, tables. 2000-2500 words. Use ACTUAL requirement data, NOT placeholders.

Return complete PRD."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert Product Manager who creates comprehensive, professional PRDs. Use proper templates and fill with actual requirement data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=3000  # Optimized for faster response
            )
            
            prd_content = response.choices[0].message.content.strip()
            print(f"[OK] PRD generated using OpenAI ({len(prd_content)} characters)")
            return prd_content
            
        except Exception as e:
            print(f"[WARNING] OpenAI PRD generation failed: {str(e)}")
            print("Falling back to template-based PRD")
            
            # Fallback: Generate basic template-based PRD
            return self._generate_fallback_prd(project_info, all_reqs)

    async def _generate_brd(self, data: Dict[str, Any]) -> str:
        """
        Generate Business Requirements Document using OpenAI based on collected requirements.
        Uses proper template structure and dynamically fills with analyzed requirement data.
        """
        # Extract requirements and project info
        requirements = data.get('requirements', [])
        gherkin_reqs = data.get('gherkinRequirements', [])
        project_info = data.get('project', {})
        risks = data.get('risks', [])
        
        print(f"[INFO] Generating BRD using OpenAI for project: {project_info.get('name', 'Project')}")
        
        # Prepare requirements summary for OpenAI
        req_summary = ""
        all_reqs = gherkin_reqs or requirements
        
        for idx, req in enumerate(all_reqs, 1):
            if isinstance(req, dict):
                req_summary += f"\n{idx}. **{req.get('feature', req.get('title', 'Requirement'))}**\n"
                if 'as_a' in req:
                    req_summary += f"   - Business Value: {req.get('so_that', 'Business value to be defined')}\n"
                    req_summary += f"   - Priority: {req.get('priority', 'Medium')}\n"
        
        if not req_summary:
            # Fallback to basic BRD if no requirements
            print("[WARNING] No requirements found, generating basic BRD template")
            return f"""# Business Requirements Document (BRD)

## Project: {project_info.get('name', 'Project')}

**Note**: This is a template BRD. Please add requirements to Phase 1 and regenerate for a complete document.

## 1. Executive Summary
{project_info.get('description', 'Business case to be added')}

## 2. Business Requirements
No requirements have been collected yet. Please complete Phase 1 (Requirements Gathering) first.

---
*Generated by TAO SDLC AI Copilot*"""
        
        # Create OpenAI prompt for intelligent BRD generation (optimized for speed)
        prompt = f"""Generate a professional Business Requirements Document (BRD) for this project.

**Project**: {project_info.get('name', 'Project')}
**Description**: {project_info.get('description', 'Business initiative')}

**Requirements**:
{req_summary}

**Include these sections with ACTUAL data from requirements**:
1. Executive Summary (2-3 paragraphs - business case, benefits, objectives)
2. Business Context (drivers, problems solved, strategic alignment)
3. Business Objectives (SMART goals tied to actual requirements)
4. Stakeholders (who's impacted, their interests)
5. Project Scope (In-Scope: ACTUAL features | Out-of-Scope)
6. Business Requirements (for each: capability, business value, priority - use ACTUAL data)
7. Business Rules & Constraints
8. Success Criteria & KPIs (measurable indicators)
9. Timeline Estimate (phases, duration)
10. Risk Analysis (business risks, mitigation)

**Format**: Professional markdown, 1500-2000 words, focus on BUSINESS VALUE. Use ACTUAL requirement data, NOT placeholders.

Return complete BRD."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert Business Analyst who creates professional BRDs focused on business value."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2200  # Optimized for faster response
            )
            
            brd_content = response.choices[0].message.content.strip()
            print(f"[OK] BRD generated using OpenAI ({len(brd_content)} characters)")
            return brd_content
            
        except Exception as e:
            print(f"[WARNING] OpenAI BRD generation failed: {str(e)}")
            print("Falling back to template-based BRD")
            
            # Fallback: Generate basic template-based BRD
            return self._generate_fallback_brd(project_info, all_reqs)

    def _generate_requirements(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate extracted requirements"""
        return [
            {
                "title": "User Authentication & Authorization",
                "priority": "High",
                "status": "documented",
                "description": "Implement secure login system with role-based access control"
            },
            {
                "title": "AI-Powered Document Generation",
                "priority": "High",
                "status": "documented",
                "description": "Generate PRD, BRD, and other documents using AI"
            },
            {
                "title": "Multi-Level Approval Workflow",
                "priority": "High",
                "status": "in_review",
                "description": "Configurable approval chains for each phase"
            },
            {
                "title": "Real-Time Collaboration",
                "priority": "Medium",
                "status": "draft",
                "description": "Enable team members to collaborate in real-time"
            },
            {
                "title": "Integration Hub",
                "priority": "Medium",
                "status": "documented",
                "description": "Connect with Jira, GitHub, Confluence, and CI/CD tools"
            }
        ]
    
    async def _generate_epics(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate epics based on Phase 1 requirements, PRD, and BRD using OpenAI
        
        Intelligently analyzes requirements and groups them into high-level epics
        """
        requirements = data.get('requirements', [])
        gherkin_reqs = data.get('gherkinRequirements', [])
        prd = data.get('prd', '')
        brd = data.get('brd', '')
        project_info = data.get('project', {})
        
        if not requirements and not gherkin_reqs:
            # Return generic epics if no requirements available
            return [
                {
                    "id": 1,
                    "title": "Core System Features",
                    "description": "Implement core system functionality",
                    "stories": 5,
                    "points": 21,
                    "priority": "High",
                    "requirements_mapped": []
                }
            ]
        
        # Prepare requirements context for OpenAI
        requirements_context = ""
        
        if gherkin_reqs:
            requirements_context += "\n### Gherkin Requirements:\n"
            for idx, req in enumerate(gherkin_reqs, 1):
                requirements_context += f"\n{idx}. **{req.get('feature', 'Feature')}** (ID: {req.get('id', '')})\n"
                requirements_context += f"   - As a {req.get('as_a', 'user')}, I want {req.get('i_want', '')}\n"
                requirements_context += f"   - So that {req.get('so_that', '')}\n"
                requirements_context += f"   - Priority: {req.get('priority', 'Medium')}\n"
                
                scenarios = req.get('scenarios', [])
                if scenarios:
                    requirements_context += f"   - Scenarios: {len(scenarios)}\n"
                    for scenario in scenarios[:2]:  # Include first 2 scenarios as examples
                        requirements_context += f"     * {scenario.get('title', '')}\n"
        
        if requirements:
            requirements_context += "\n### Legacy Requirements:\n"
            for idx, req in enumerate(requirements, 1):
                requirements_context += f"{idx}. {req.get('title', 'Requirement')} (Priority: {req.get('priority', 'Medium')})\n"
        
        # Extract key sections from PRD and BRD for context
        prd_summary = ""
        if prd and len(prd) > 100:
            # Extract first 2000 characters of PRD for context
            prd_summary = prd[:2000] + "..."
        
        brd_summary = ""
        if brd and len(brd) > 100:
            # Extract first 2000 characters of BRD for context
            brd_summary = brd[:2000] + "..."
        
        # Create prompt for OpenAI to generate epics
        prompt = f"""You are an expert Product Manager and Agile Coach. Analyze the following requirements from Phase 1 (Requirements Gathering) and generate a comprehensive set of Epics for Phase 2 (Planning & Backlog).

**Project**: {project_info.get('name', 'Software Project')}

**Business Requirements Document (BRD) Summary**:
{brd_summary if brd_summary else "Not provided"}

**Product Requirements Document (PRD) Summary**:
{prd_summary if prd_summary else "Not provided"}

{requirements_context}

**Instructions**:
1. Analyze all the requirements, PRD, and BRD provided above
2. Group related requirements into logical, high-level Epics (typically 3-6 epics)
3. Each epic should represent a major feature area or business capability
4. Ensure EVERY requirement is mapped to an epic (use the requirement IDs)
5. Estimate the number of user stories (2-10) and story points (10-50) for each epic based on complexity
6. Assign priority based on business value: High, Medium, or Low
7. Create meaningful titles and descriptions that reflect the actual requirements

**Output Format** (JSON array):
[
  {{
    "id": 1,
    "title": "Epic Name",
    "description": "Detailed description of what this epic covers",
    "stories": 5,
    "points": 25,
    "priority": "High",
    "requirements_mapped": ["req-id-1", "req-id-2"]
  }}
]

Return ONLY the JSON array, no additional text."""

        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert Product Manager who creates well-structured Epics from requirements. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            epics = json.loads(content)
            
            # Validate and ensure proper structure
            if isinstance(epics, list) and len(epics) > 0:
                # Ensure all epics have required fields
                for epic in epics:
                    if 'id' not in epic:
                        epic['id'] = epics.index(epic) + 1
                    if 'title' not in epic:
                        epic['title'] = f"Epic {epic['id']}"
                    if 'description' not in epic:
                        epic['description'] = "Epic description"
                    if 'stories' not in epic:
                        epic['stories'] = 5
                    if 'points' not in epic:
                        epic['points'] = epic['stories'] * 5
                    if 'priority' not in epic:
                        epic['priority'] = "Medium"
                    if 'requirements_mapped' not in epic:
                        epic['requirements_mapped'] = []
                
                print(f"[OK] Generated {len(epics)} epics using OpenAI")
                return epics
            else:
                raise ValueError("Invalid epic structure from OpenAI")
                
        except Exception as e:
            print(f"[WARNING] Error generating epics with OpenAI: {str(e)}")
            print(f"Falling back to template-based generation")
            
            # Fallback: Create simplified epics from requirements
            epics = []
            epic_id = 1
            
            if gherkin_reqs:
                # Group requirements into 3-4 epics
                reqs_per_epic = max(2, len(gherkin_reqs) // 3)
                
                for i in range(0, len(gherkin_reqs), reqs_per_epic):
                    batch = gherkin_reqs[i:i+reqs_per_epic]
                    if not batch:
                        continue
                    
                    title = batch[0].get('feature', f'Epic {epic_id}')
                    num_stories = min(10, len(batch) * 2)
                    estimated_points = num_stories * 5
                    
                    epic = {
                        "id": epic_id,
                        "title": title,
                        "description": f"Implementation of {len(batch)} related requirements",
                        "stories": num_stories,
                        "points": estimated_points,
                        "priority": "High",
                        "requirements_mapped": [req.get('id', f'req-{i}') for req in batch]
                    }
                    epics.append(epic)
                    epic_id += 1
                    
                    if epic_id > 4:
                        break
        
            return epics if epics else [
                {
                    "id": 1,
                    "title": "Core System Features",
                    "description": "Implement core system functionality",
                    "stories": 5,
                    "points": 25,
                    "priority": "High",
                    "requirements_mapped": []
                }
            ]
    
    async def _generate_user_stories(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate user stories based on epics and Gherkin requirements using OpenAI
        
        Creates detailed user stories with acceptance criteria from actual requirements
        """
        epics = data.get('epics', [])
        gherkin_reqs = data.get('gherkinRequirements', [])
        requirements = data.get('requirements', [])
        prd = data.get('prd', '')
        brd = data.get('brd', '')
        project_info = data.get('project', {})
        
        if not epics:
            # Need epics first to generate stories
            return []
        
        # Prepare context for OpenAI
        epics_context = ""
        for epic in epics:
            epics_context += f"\n**Epic {epic.get('id')}**: {epic.get('title')}\n"
            epics_context += f"  - Description: {epic.get('description')}\n"
            epics_context += f"  - Priority: {epic.get('priority')}\n"
            epics_context += f"  - Expected Stories: {epic.get('stories')}\n"
            epics_context += f"  - Story Points: {epic.get('points')}\n"
            epics_context += f"  - Requirements Mapped: {', '.join(epic.get('requirements_mapped', []))}\n"
        
        # Prepare requirements context
        requirements_context = ""
        if gherkin_reqs:
            requirements_context += "\n### Gherkin Requirements:\n"
            for req in gherkin_reqs:
                requirements_context += f"\n**{req.get('feature')}** (ID: {req.get('id')})\n"
                requirements_context += f"  - As a {req.get('as_a')}, I want {req.get('i_want')}\n"
                requirements_context += f"  - So that {req.get('so_that')}\n"
                
                scenarios = req.get('scenarios', [])
                if scenarios:
                    requirements_context += f"  - Scenarios:\n"
                    for scenario in scenarios:
                        requirements_context += f"    * {scenario.get('title')}\n"
                        if scenario.get('given'):
                            requirements_context += f"      - Given: {', '.join(scenario.get('given'))}\n"
                        if scenario.get('when'):
                            requirements_context += f"      - When: {', '.join(scenario.get('when'))}\n"
                        if scenario.get('then'):
                            requirements_context += f"      - Then: {', '.join(scenario.get('then'))}\n"
        
        # Create prompt for OpenAI
        prompt = f"""You are an expert Agile Scrum Master and Product Owner. Based on the Epics created in Phase 2 (Planning & Backlog) and the requirements from Phase 1, generate detailed User Stories with acceptance criteria.

**Project**: {project_info.get('name', 'Software Project')}

## Epics Generated:
{epics_context}

## Requirements from Phase 1:
{requirements_context}

**Instructions**:
1. For EACH Epic, generate user stories that match the "Expected Stories" count
2. Base stories on the actual requirements mapped to each epic (use the requirement IDs)
3. Each story should follow the format: "As a [role], I want [goal], so that [benefit]"
4. Include detailed acceptance criteria derived from the Gherkin scenarios (Given-When-Then)
5. Estimate story points using Fibonacci scale: 1, 2, 3, 5, 8, 13
6. Assign priority: High, Medium, or Low based on the epic priority and requirement priority
7. All stories should be in "backlog" status with no sprint assigned initially
8. Stories should cover: core functionality, UI/UX, testing, integration, security, error handling, and documentation

**Output Format** (JSON array):
[
  {{
    "id": 1,
    "epic": "Epic Title",
    "epic_id": 1,
    "title": "As a user, I want to...",
    "description": "Detailed description of what needs to be done",
    "acceptance_criteria": ["Criterion 1", "Criterion 2", "Criterion 3"],
    "points": 5,
    "priority": "High",
    "sprint": null,
                            "status": "backlog"
  }}
]

Return ONLY the JSON array with all user stories, no additional text."""

        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert Scrum Master who creates detailed user stories from epics and requirements. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            user_stories = json.loads(content)
            
            # Validate and ensure proper structure
            if isinstance(user_stories, list) and len(user_stories) > 0:
                story_id = 1
                for story in user_stories:
                    # Ensure required fields
                    story['id'] = story_id
                    story_id += 1
                    
                    if 'epic' not in story:
                        story['epic'] = "Unknown Epic"
                    if 'epic_id' not in story:
                        story['epic_id'] = 1
                    if 'title' not in story:
                        story['title'] = "User Story"
                    if 'description' not in story:
                        story['description'] = "Story description"
                    if 'acceptance_criteria' not in story:
                        story['acceptance_criteria'] = []
                    if 'points' not in story:
                        story['points'] = 5
                    if 'priority' not in story:
                        story['priority'] = "Medium"
                    if 'sprint' not in story:
                        story['sprint'] = None
                    if 'status' not in story:
                        story['status'] = "backlog"
                
                print(f"[OK] Generated {len(user_stories)} user stories using OpenAI")
                return user_stories
            else:
                raise ValueError("Invalid user story structure from OpenAI")
                
        except Exception as e:
            print(f"[WARNING] Error generating user stories with OpenAI: {str(e)}")
            print(f"Falling back to template-based generation")
            
            # Fallback: Generate basic stories from epics
            user_stories = []
            story_id = 1
            
            for epic in epics:
                epic_id = epic.get('id', 0)
                epic_title = epic.get('title', 'Epic')
                num_stories = epic.get('stories', 5)
                points_per_story = max(3, epic.get('points', 25) // num_stories)
                
                for i in range(min(num_stories, 5)):  # Limit to 5 stories per epic in fallback
                    story = {
                        "id": story_id,
                        "epic": epic_title,
                        "epic_id": epic_id,
                        "title": f"As a user, I want to use {epic_title.lower()} functionality",
                        "description": f"Implement core functionality for {epic_title}",
                        "acceptance_criteria": [
                            f"{epic_title} is implemented as specified",
                            "All features are accessible and functional",
                            "Error handling is robust"
                        ],
                        "points": min(points_per_story, 8),
                        "priority": epic.get('priority', 'Medium'),
                        "sprint": None,
                        "status": "backlog"
                    }
                    user_stories.append(story)
                    story_id += 1
        
        return user_stories
    
    def _estimate_story_points(self, description: str, scenarios: List[Dict]) -> int:
        """
        Estimate story points based on complexity
        
        Fibonacci scale: 1, 2, 3, 5, 8, 13
        """
        # Base points
        points = 3
        
        # Add points based on number of scenarios
        num_scenarios = len(scenarios)
        if num_scenarios > 3:
            points = 8
        elif num_scenarios > 2:
            points = 5
        elif num_scenarios > 1:
            points = 3
        else:
            points = 2
        
        # Add points for complexity keywords
        complexity_keywords = ['integrate', 'api', 'payment', 'security', 'authentication', 'sync', 'complex']
        desc_lower = description.lower()
        
        if any(keyword in desc_lower for keyword in complexity_keywords):
            points += 2
        
        # Cap at 13 (anything larger should be broken down)
        return min(points, 13)
    
    def _generate_architecture(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate system architecture based on epics and user stories
        
        Creates architecture components, technology stack, database design, and API design
        """
        epics = data.get('epics', [])
        user_stories = data.get('userStories', [])
        
        if not epics:
            # Return default architecture if no epics
            return {
                "components": [
                    {
                        "id": 1,
                        "name": "Frontend Application",
                        "type": "frontend",
                        "description": "User-facing web application",
                        "technologies": ["React", "TypeScript", "Tailwind CSS"]
                    },
                    {
                        "id": 2,
                        "name": "Backend API",
                        "type": "backend",
                        "description": "RESTful API server",
                        "technologies": ["Node.js", "Express", "PostgreSQL"]
                    }
                ],
                "techStack": {
                    "frontend": ["React", "TypeScript", "Tailwind CSS"],
                    "backend": ["Node.js", "Express", "JWT"],
                    "infrastructure": ["Docker", "AWS", "PostgreSQL"]
                },
                "database": {},
                "api": {}
            }
        
        # Generate architecture components based on epics
        components = []
        component_id = 1
        
        # Core components
        components.append({
            "id": component_id,
            "name": "Frontend Application",
            "type": "frontend",
            "description": "User-facing web application with responsive design",
            "technologies": ["React", "TypeScript", "Tailwind CSS", "Vite"]
        })
        component_id += 1
        
        components.append({
            "id": component_id,
            "name": "Backend API Server",
            "type": "backend",
            "description": "RESTful API handling business logic and data management",
            "technologies": ["FastAPI", "Python", "Pydantic", "SQLAlchemy"]
        })
        component_id += 1
        
        components.append({
            "id": component_id,
            "name": "PostgreSQL Database",
            "type": "database",
            "description": "Primary data storage with relational schema",
            "technologies": ["PostgreSQL", "pgVector", "Alembic"]
        })
        component_id += 1
        
        # Check for specific features from epics and add components
        epic_titles = [epic.get('title', '').lower() for epic in epics]
        all_epic_text = ' '.join(epic_titles)
        
        if any(word in all_epic_text for word in ['auth', 'login', 'user', 'security']):
            components.append({
                "id": component_id,
                "name": "Authentication Service",
                "type": "security",
                "description": "User authentication and authorization system",
                "technologies": ["JWT", "bcrypt", "OAuth 2.0", "Session Management"]
            })
            component_id += 1
        
        if any(word in all_epic_text for word in ['payment', 'billing', 'subscription']):
            components.append({
                "id": component_id,
                "name": "Payment Gateway Integration",
                "type": "integration",
                "description": "Payment processing and billing management",
                "technologies": ["Stripe API", "Webhook Handler", "PCI Compliance"]
            })
            component_id += 1
        
        if any(word in all_epic_text for word in ['notification', 'email', 'alert']):
            components.append({
                "id": component_id,
                "name": "Notification Service",
                "type": "service",
                "description": "Email and push notification delivery system",
                "technologies": ["SendGrid", "Redis Queue", "WebSocket"]
            })
            component_id += 1
        
        if any(word in all_epic_text for word in ['search', 'analytics', 'dashboard']):
            components.append({
                "id": component_id,
                "name": "Analytics & Reporting",
                "type": "service",
                "description": "Data analytics and reporting engine",
                "technologies": ["Elasticsearch", "Grafana", "Pandas"]
            })
            component_id += 1
        
        if any(word in all_epic_text for word in ['ai', 'ml', 'copilot', 'chatbot']):
            components.append({
                "id": component_id,
                "name": "AI/ML Service",
                "type": "service",
                "description": "AI-powered features and intelligent automation",
                "technologies": ["OpenAI API", "LangChain", "Vector Database", "RAG"]
            })
            component_id += 1
        
        # Generate technology stack
        tech_stack = {
            "frontend": [
                "React 18",
                "TypeScript",
                "Tailwind CSS",
                "Vite",
                "React Router",
                "Zustand"
            ],
            "backend": [
                "FastAPI",
                "Python 3.11+",
                "SQLAlchemy",
                "Pydantic",
                "JWT Auth",
                "CORS Middleware"
            ],
            "database": [
                "PostgreSQL 15+",
                "Redis (Cache)",
                "pgVector (AI)",
                "Alembic (Migrations)"
            ],
            "infrastructure": [
                "Docker",
                "Docker Compose",
                "AWS EC2 / DigitalOcean",
                "Nginx",
                "GitHub Actions"
            ],
            "testing": [
                "Pytest",
                "Jest",
                "React Testing Library",
                "Playwright"
            ]
        }
        
        # Generate database schema overview
        database_schema = {
            "tables": [
                {
                    "name": "users",
                    "description": "User accounts and authentication",
                    "key_fields": ["id", "email", "username", "password_hash", "role"]
                },
                {
                    "name": "projects",
                    "description": "Project information",
                    "key_fields": ["id", "name", "description", "created_by", "status"]
                },
                {
                    "name": "phases",
                    "description": "SDLC phases per project",
                    "key_fields": ["id", "project_id", "phase_number", "status", "data"]
                }
            ]
        }
        
        # Generate API design overview
        api_design = {
            "restful_endpoints": [
                {"method": "POST", "path": "/api/auth/login", "description": "User authentication"},
                {"method": "GET", "path": "/api/projects", "description": "List all projects"},
                {"method": "POST", "path": "/api/projects", "description": "Create new project"},
                {"method": "GET", "path": "/api/projects/{id}", "description": "Get project details"},
                {"method": "GET", "path": "/api/projects/{id}/phases", "description": "Get project phases"}
            ],
            "authentication": "JWT Bearer Token",
            "data_format": "JSON",
            "versioning": "URL path (/api/v1/...)"
        }
        
        return {
            "components": components,
            "techStack": tech_stack,
            "database": database_schema,
            "api": api_design
        }
    
    async def convert_to_gherkin(self, parsed_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert parsed document content to Gherkin format requirements using OpenAI
        
        Intelligently reads, analyzes, and extracts requirements from uploaded documents
        
        Args:
            parsed_content: Parsed document content from DocumentParser
            
        Returns:
            List of requirements in proper Gherkin format
        """
        # Extract text content
        text = parsed_content.get('text', '')
        filename = parsed_content.get('filename', 'document')
        
        if not text or len(text.strip()) < 20:
            # Text too short, return empty
            return []
        
        # Prepare comprehensive prompt for OpenAI
        prompt = f"""You are an expert Business Analyst and Requirements Engineer. Analyze the following document and extract ALL requirements in proper Gherkin format.

**Document**: {filename}

**Content**:
{text[:8000]}  

**Your Task**:
1. **READ** the entire document carefully
2. **ANALYZE** and identify all functional and non-functional requirements
3. **SUMMARIZE** each requirement clearly
4. **EXTRACT** requirements and convert to proper Gherkin format
5. **PRIORITIZE** each requirement (Critical/High/Medium/Low) based on:
   - Business impact
   - User value
   - Technical complexity
   - Dependencies

**Instructions**:
- Extract EVERY requirement mentioned in the document
- For each requirement, create:
  * Clear Feature name
  * User story in format: "As a [role], I want [goal], so that [benefit]"
  * Multiple realistic scenarios with Given-When-Then
  * Priority based on importance indicators in document
  * Status as "draft"
- Include:
  * Functional requirements (what the system should do)
  * User interactions
  * Business rules
  * Data requirements
  * Integration needs
  * Security requirements
  * Performance requirements
- Make scenarios specific and testable
- Use actual details from the document, not generic placeholders

**Output Format** (JSON array):
[
  {{
    "id": "req-1",
    "feature": "Specific Feature Name from Document",
    "as_a": "specific user role from document",
    "i_want": "specific goal from document",
    "so_that": "specific benefit from document",
    "scenarios": [
      {{
        "title": "Specific scenario from document",
        "given": ["specific precondition 1", "specific precondition 2"],
        "when": ["specific action 1", "specific action 2"],
        "then": ["specific expected result 1", "specific expected result 2"]
      }}
    ],
    "priority": "Critical|High|Medium|Low",
    "status": "draft",
    "notes": "Any important notes or clarifications from document"
  }}
]

Return ONLY the JSON array with ALL extracted requirements. Be thorough and extract everything mentioned in the document."""

        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert Business Analyst who extracts and converts requirements into proper Gherkin format. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent extraction
                max_tokens=4000
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            gherkin_requirements = json.loads(content)
            
            # Validate and ensure proper structure
            if isinstance(gherkin_requirements, list) and len(gherkin_requirements) > 0:
                for idx, req in enumerate(gherkin_requirements):
                    # Ensure required fields
                    if 'id' not in req:
                        req['id'] = f"req-{idx + 1}"
                    if 'feature' not in req:
                        req['feature'] = f"Requirement {idx + 1}"
                    if 'as_a' not in req:
                        req['as_a'] = "user"
                    if 'i_want' not in req:
                        req['i_want'] = "to use this feature"
                    if 'so_that' not in req:
                        req['so_that'] = "I can achieve my goals"
                    if 'scenarios' not in req or not req['scenarios']:
                        req['scenarios'] = [{
                            'title': 'Default scenario',
                            'given': ['preconditions are met'],
                            'when': ['user performs action'],
                            'then': ['expected result occurs']
                        }]
                    if 'priority' not in req:
                        req['priority'] = "Medium"
                    if 'status' not in req:
                        req['status'] = "draft"
                
                print(f"[OK] Extracted {len(gherkin_requirements)} requirements from document using OpenAI")
                return gherkin_requirements
            else:
                raise ValueError("Invalid requirements structure from OpenAI")
                
        except Exception as e:
            print(f"[WARNING] Error extracting requirements with OpenAI: {str(e)}")
            print("Falling back to basic extraction")
            
            # Fallback: Basic extraction
            return [{
                'id': 'req-1',
                'feature': f'Requirements from {filename}',
                'as_a': 'user',
                'i_want': 'to implement the requirements from the uploaded document',
                'so_that': 'the system meets the documented needs',
                'scenarios': [{
                    'title': 'Review extracted content',
                    'given': ['document has been uploaded'],
                    'when': ['requirements are extracted'],
                    'then': ['requirements are available for review']
                }],
                'priority': 'Medium',
                'status': 'draft',
                'notes': f'Please review the uploaded document manually. Auto-extraction encountered an issue: {str(e)}'
            }]
    
    async def generate_prd_from_requirements(self, requirements: List[Dict[str, Any]], project_name: str = "Project") -> str:
        """
        Generate Product Requirements Document from extracted requirements using OpenAI
        
        Args:
            requirements: List of Gherkin requirements
            project_name: Name of the project
            
        Returns:
            Complete PRD document in markdown format
        """
        # Prepare requirements summary
        req_summary = ""
        for idx, req in enumerate(requirements, 1):
            req_summary += f"\n{idx}. **{req.get('feature', 'Feature')}**\n"
            req_summary += f"   - As a {req.get('as_a', 'user')}, I want {req.get('i_want', '')}\n"
            req_summary += f"   - So that {req.get('so_that', '')}\n"
            req_summary += f"   - Priority: {req.get('priority', 'Medium')}\n"
            
            scenarios = req.get('scenarios', [])
            if scenarios:
                req_summary += f"   - Scenarios: {len(scenarios)}\n"
        
        prompt = f"""You are an expert Product Manager. Generate a comprehensive Product Requirements Document (PRD) based on the following extracted requirements.

**Project**: {project_name}

**Extracted Requirements**:
{req_summary}

**Instructions**:
Generate a complete, professional PRD following industry best practices with these sections:

1. **Executive Summary**: Overview and objectives
2. **Product Overview**: What is being built and why
3. **Target Users**: Who will use this product
4. **User Personas**: 2-3 detailed personas based on requirements
5. **Feature Requirements**: Detailed breakdown of each feature from extracted requirements
   - Use the actual requirement details
   - Include user stories
   - Add acceptance criteria from scenarios
6. **Functional Requirements**: System capabilities
7. **Non-Functional Requirements**: Performance, security, scalability
8. **User Experience**: UI/UX considerations
9. **Technical Considerations**: Tech stack suggestions
10. **Success Metrics**: KPIs and measurement criteria
11. **Timeline & Phases**: Suggested development phases
12. **Risks & Mitigations**: Potential challenges

**Format**: Markdown with proper headings, lists, and formatting
**Style**: Professional, clear, actionable
**Length**: Comprehensive (2000-3000 words)

Use the ACTUAL requirement details provided above. Do not use generic placeholders. Make it specific to the extracted requirements.

Return the complete PRD document in markdown format."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert Product Manager who creates comprehensive PRDs. Write in markdown format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=4000
            )
            
            prd_content = response.choices[0].message.content.strip()
            print(f"[OK] Generated PRD from {len(requirements)} requirements using OpenAI")
            return prd_content
            
        except Exception as e:
            print(f"[WARNING] Error generating PRD with OpenAI: {str(e)}")
            # Return basic PRD
            return self._generate_prd({'requirements': [], 'gherkinRequirements': requirements, 'project': {'name': project_name}})
    
    async def generate_brd_from_requirements(self, requirements: List[Dict[str, Any]], project_name: str = "Project") -> str:
        """
        Generate Business Requirements Document from extracted requirements using OpenAI
        
        Args:
            requirements: List of Gherkin requirements
            project_name: Name of the project
            
        Returns:
            Complete BRD document in markdown format
        """
        # Prepare requirements summary
        req_summary = ""
        for idx, req in enumerate(requirements, 1):
            req_summary += f"\n{idx}. **{req.get('feature', 'Feature')}** (Priority: {req.get('priority', 'Medium')})\n"
            req_summary += f"   - User Story: As a {req.get('as_a', 'user')}, I want {req.get('i_want', '')}\n"
            req_summary += f"   - Business Value: {req.get('so_that', '')}\n"
        
        prompt = f"""You are an expert Business Analyst. Generate a comprehensive Business Requirements Document (BRD) based on the following extracted requirements.

**Project**: {project_name}

**Extracted Requirements**:
{req_summary}

**Instructions**:
Generate a complete, professional BRD following industry best practices with these sections:

1. **Executive Summary**: Business case and objectives
2. **Business Context**: Industry, market, and competitive landscape
3. **Business Objectives**: Clear, measurable goals (SMART)
4. **Stakeholders**: Key stakeholders and their interests
5. **Scope**: In-scope and out-of-scope items based on requirements
6. **Business Requirements**: High-level business needs
   - Use the actual extracted requirements
   - Group by business capability
   - Link to business value
7. **Functional Requirements**: Detailed functionality needed
8. **Business Rules**: Rules and constraints
9. **Assumptions & Dependencies**: What we're assuming, what we depend on
10. **Success Criteria**: How we measure success
11. **Timeline & Budget**: High-level estimates
12. **Risk Analysis**: Business risks and mitigation strategies
13. **Approval & Sign-off**: Stakeholder approval process

**Format**: Markdown with proper headings, tables, and formatting
**Style**: Business-focused, strategic, clear
**Length**: Comprehensive (2000-3000 words)

Use the ACTUAL requirement details provided above. Focus on BUSINESS VALUE and strategic alignment. Make it specific to the extracted requirements.

Return the complete BRD document in markdown format."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert Business Analyst who creates comprehensive BRDs. Write in markdown format focusing on business value."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=4000
            )
            
            brd_content = response.choices[0].message.content.strip()
            print(f"[OK] Generated BRD from {len(requirements)} requirements using OpenAI")
            return brd_content
            
        except Exception as e:
            print(f"[WARNING] Error generating BRD with OpenAI: {str(e)}")
            # Return basic BRD
            return self._generate_brd({'requirements': [], 'gherkinRequirements': requirements, 'project': {'name': project_name}})
    
    async def analyze_risks(self, requirements: List[Dict[str, Any]], project_name: str = "Project") -> List[Dict[str, Any]]:
        """
        Analyze risks based on extracted requirements using OpenAI.
        Returns list of risks with priority, impact, and mitigation strategies.
        
        Args:
            requirements: List of Gherkin requirements
            project_name: Name of the project
            
        Returns:
            List of risk assessments
        """
        if not requirements:
            return []
        
        # Prepare requirements summary for risk analysis
        req_summary = ""
        for idx, req in enumerate(requirements, 1):
            req_summary += f"\n{idx}. **{req.get('feature', 'Feature')}**\n"
            req_summary += f"   - Priority: {req.get('priority', 'Medium')}\n"
            req_summary += f"   - User Story: As a {req.get('as_a', 'user')}, I want {req.get('i_want', '')}\n"
            
            scenarios = req.get('scenarios', [])
            if scenarios:
                req_summary += f"   - Complexity: {len(scenarios)} scenarios\n"
        
        prompt = f"""You are an expert Risk Analyst and Project Manager. Analyze the following requirements and identify potential risks for this project.

**Project**: {project_name}

**Requirements**:
{req_summary}

**Instructions**:
Analyze these requirements and identify risks in the following categories:
1. **Technical Risks**: Technology challenges, integration issues, performance concerns
2. **Business Risks**: Market changes, stakeholder alignment, ROI concerns
3. **Resource Risks**: Team availability, skills gaps, dependencies
4. **Schedule Risks**: Timeline pressures, dependencies, scope creep
5. **Quality Risks**: Testing challenges, complexity, technical debt

For each risk, provide:
- **Risk Name**: Clear, specific risk description
- **Category**: Technical/Business/Resource/Schedule/Quality
- **Priority**: Critical/High/Medium/Low (based on likelihood × impact)
- **Impact**: Severe/High/Medium/Low
- **Likelihood**: Very Likely/Likely/Possible/Unlikely
- **Mitigation**: Specific mitigation strategy
- **Contingency**: What to do if risk occurs

**Priority Calculation**:
- Critical: High likelihood + High/Severe impact
- High: Medium/High likelihood + Medium/High impact
- Medium: Low/Medium likelihood + Medium impact
- Low: Low likelihood + Low impact

**Output Format** (JSON array):
[
  {{
    "id": "risk-1",
    "risk": "Specific risk description",
    "category": "Technical|Business|Resource|Schedule|Quality",
    "priority": "Critical|High|Medium|Low",
    "impact": "Severe|High|Medium|Low",
    "likelihood": "Very Likely|Likely|Possible|Unlikely",
    "mitigation": "Specific mitigation strategy",
    "contingency": "Plan if risk occurs",
    "affected_requirements": ["req-1", "req-2"]
  }}
]

Identify 5-10 most significant risks. Be specific to the actual requirements provided. Focus on realistic, actionable risks.

Return ONLY the JSON array."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert Risk Analyst who identifies and assesses project risks. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,  # Lower temperature for more consistent risk analysis
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            risks = json.loads(content)
            
            # Validate and ensure proper structure
            if isinstance(risks, list):
                for idx, risk in enumerate(risks):
                    if 'id' not in risk:
                        risk['id'] = f"risk-{idx + 1}"
                    if 'risk' not in risk:
                        risk['risk'] = f"Risk {idx + 1}"
                    if 'category' not in risk:
                        risk['category'] = "Technical"
                    if 'priority' not in risk:
                        risk['priority'] = "Medium"
                    if 'impact' not in risk:
                        risk['impact'] = "Medium"
                    if 'likelihood' not in risk:
                        risk['likelihood'] = "Possible"
                    if 'mitigation' not in risk:
                        risk['mitigation'] = "To be defined"
                    if 'contingency' not in risk:
                        risk['contingency'] = "Monitor and reassess"
                    if 'affected_requirements' not in risk:
                        risk['affected_requirements'] = []
                
                print(f"[OK] Analyzed {len(risks)} risks using OpenAI")
                return risks
            else:
                raise ValueError("Invalid risk structure from OpenAI")
                
        except Exception as e:
            print(f"[WARNING] Error analyzing risks with OpenAI: {str(e)}")
            
            # Fallback: Return basic risk assessment
            return [
                {
                    "id": "risk-1",
                    "risk": "Technical complexity in implementation",
                    "category": "Technical",
                    "priority": "High",
                    "impact": "High",
                    "likelihood": "Likely",
                    "mitigation": "Conduct technical spike, use proven technologies",
                    "contingency": "Allocate additional development time",
                    "affected_requirements": []
                },
                {
                    "id": "risk-2",
                    "risk": "Resource availability constraints",
                    "category": "Resource",
                    "priority": "Medium",
                    "impact": "Medium",
                    "likelihood": "Possible",
                    "mitigation": "Ensure team allocation in advance",
                    "contingency": "Adjust timeline or scope",
                    "affected_requirements": []
                },
                {
                    "id": "risk-3",
                    "risk": "Scope creep and requirement changes",
                    "category": "Schedule",
                    "priority": "High",
                    "impact": "High",
                    "likelihood": "Likely",
                    "mitigation": "Implement strict change control process",
                    "contingency": "Re-prioritize features, phase delivery",
                    "affected_requirements": []
                }
            ]
    
    def _generate_fallback_prd(self, project_info: Dict[str, Any], requirements: List[Dict[str, Any]]) -> str:
        """Generate basic PRD when OpenAI fails"""
        features_section = ""
        for idx, req in enumerate(requirements, 1):
            feature_name = req.get('feature', req.get('title', f'Feature {idx}'))
            priority = req.get('priority', 'Medium')
            features_section += f"\n### {idx}. {feature_name}\n**Priority**: {priority}\n\n"
        
        return f"""# Product Requirements Document (PRD)

## Project: {project_info.get('name', 'Project')}

## 1. Product Overview
{project_info.get('description', 'Product description')}

## 2. Key Features
{features_section}

## 3. Requirements Summary
Total Requirements: {len(requirements)}

---
*Generated by TAO SDLC AI Copilot (Fallback Mode)*"""
    
    def _generate_fallback_brd(self, project_info: Dict[str, Any], requirements: List[Dict[str, Any]]) -> str:
        """Generate basic BRD when OpenAI fails"""
        scope_items = ""
        for idx, req in enumerate(requirements, 1):
            feature_name = req.get('feature', req.get('title', f'Feature {idx}'))
            priority = req.get('priority', 'Medium')
            scope_items += f"- {feature_name} (Priority: {priority})\n"
        
        return f"""# Business Requirements Document (BRD)

## Project: {project_info.get('name', 'Project')}

## 1. Executive Summary
{project_info.get('description', 'Business case')}

## 2. Business Objectives
- Deliver high-quality solution meeting all requirements
- Ensure user satisfaction and adoption
- Achieve ROI within expected timeframe

## 3. Scope

### In Scope
{scope_items}

## 4. Requirements Summary
Total Requirements: {len(requirements)}

---
*Generated by TAO SDLC AI Copilot (Fallback Mode)*"""

