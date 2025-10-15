from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class PhaseStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"

class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"

class IntegrationType(str, enum.Enum):
    JIRA = "jira"
    GITHUB = "github"
    GITLAB = "gitlab"
    CONFLUENCE = "confluence"
    SLACK = "slack"
    TEAMS = "teams"
    JENKINS = "jenkins"
    CIRCLECI = "circleci"

class WorkflowType(str, enum.Enum):
    CODE_GENERATION = "code_generation"
    TEST_GENERATION = "test_generation"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    CODE_REVIEW = "code_review"

# Phase configurations
PHASE_CONFIGS = {
    1: {
        "name": "Requirements & Business Analysis",
        "description": "Define what to build",
        "key_activities": ["Requirements Collection", "PRD/BRD Creation", "Feasibility Analysis", "Risk Assessment"],
        "deliverables": ["PRD", "BRD", "Risk Assessment"],
        "approvers": ["BR Owner", "Product Owner", "Business Stakeholders"]
    },
    2: {
        "name": "Planning & Product Backlog",
        "description": "Plan how much and when",
        "key_activities": ["Effort Estimation", "Backlog Creation", "Sprint Planning", "Resource Allocation"],
        "deliverables": ["Product Backlog", "Sprint Plan", "Release Roadmap"],
        "approvers": ["Project Manager", "Product Owner", "Technical Lead"]
    },
    3: {
        "name": "Architecture & High-Level Design",
        "description": "Design the overall system",
        "key_activities": ["System Architecture", "Infrastructure Design", "Security Architecture", "API Architecture"],
        "deliverables": ["Architecture Document", "Infrastructure Blueprint", "Security Plan"],
        "approvers": ["Solution Architect", "Technical Architect", "Security Architect"]
    },
    4: {
        "name": "Detailed Design & Specifications",
        "description": "Create detailed specifications",
        "key_activities": ["Database Design", "API Design", "UX/UI Design", "FSD Creation"],
        "deliverables": ["DB Schema", "API Specs", "FSD", "UX/UI Designs"],
        "approvers": ["Technical Lead", "Backend Architect", "Frontend Architect", "UX Designer"]
    },
    5: {
        "name": "Development, Testing & Code Review",
        "description": "Build and test the software",
        "key_activities": ["Backend Development", "Frontend Development", "Unit Testing", "Integration Testing", "QA", "UAT"],
        "deliverables": ["Working Software", "Test Reports", "Code Coverage Reports"],
        "approvers": ["Technical Lead", "Senior Dev", "QA Lead", "Security Team"]
    },
    6: {
        "name": "Deployment, Release & Operations",
        "description": "Release to production and monitor",
        "key_activities": ["Staging Deployment", "Production Deployment", "Monitoring Setup", "Documentation"],
        "deliverables": ["Deployed Application", "Monitoring Dashboard", "Documentation"],
        "approvers": ["DevOps Lead", "Technical Lead", "Product Owner"]
    }
}

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(String)  # BR-owner, Logical-Arc-owner, etc.
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    projects = relationship("ProjectStakeholder", back_populates="user")
    approvals = relationship("Approval", back_populates="approver")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    current_phase = Column(Integer, default=1)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    stakeholders = relationship("ProjectStakeholder", back_populates="project")
    phases = relationship("Phase", back_populates="project")

class ProjectStakeholder(Base):
    __tablename__ = "project_stakeholders"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)  # BR-owner, Logical-Arc-owner, Deployment-Arc-owner, etc.
    
    project = relationship("Project", back_populates="stakeholders")
    user = relationship("User", back_populates="projects")

class Phase(Base):
    __tablename__ = "phases"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    phase_number = Column(Integer)  # 1-6
    phase_name = Column(String)
    status = Column(Enum(PhaseStatus), default=PhaseStatus.NOT_STARTED)
    data = Column(JSON)  # Store phase-specific data
    ai_confidence_score = Column(Integer, default=0)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    estimated_hours = Column(Integer)
    actual_hours = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("Project", back_populates="phases")
    approvals = relationship("Approval", back_populates="phase")
    workflows = relationship("AutomationWorkflow", back_populates="phase")

class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    phase_id = Column(Integer, ForeignKey("phases.id"))
    approver_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    comments = Column(Text)
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    phase = relationship("Phase", back_populates="approvals")
    approver = relationship("User", back_populates="approvals")

class AIInteraction(Base):
    __tablename__ = "ai_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    phase_id = Column(Integer, ForeignKey("phases.id"))
    user_query = Column(Text)
    ai_response = Column(Text)
    confidence_score = Column(Integer)
    accepted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

