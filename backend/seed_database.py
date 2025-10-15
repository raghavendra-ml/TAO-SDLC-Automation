"""
Database Seed Script
Creates demo user and optional sample data for TAO SDLC application
"""
import sys
import os
from sqlalchemy.orm import Session
import bcrypt

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import User, Project, Phase, PhaseStatus, PHASE_CONFIGS
from app import models_integrations  # Import to register all models
from datetime import datetime

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def seed_database():
    """Seed the database with demo user and sample data"""
    print("=" * 60)
    print("TAO SDLC Database Seed Script")
    print("=" * 60)
    
    # Create all tables
    print("\n[1/4] Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return
    
    # Create database session
    db: Session = SessionLocal()
    
    try:
        # Create demo user
        print("\n[2/4] Creating demo user...")
        demo_username = "demo@tao.com"
        demo_password = "demo123"
        
        # Check if demo user already exists
        existing_user = db.query(User).filter(
            (User.email == demo_username) | (User.username == demo_username)
        ).first()
        
        if existing_user:
            print(f"✓ Demo user already exists: {demo_username}")
        else:
            demo_user = User(
                email=demo_username,
                username=demo_username,
                full_name="Demo User",
                role="Product Manager",
                hashed_password=get_password_hash(demo_password)
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            print(f"✓ Demo user created successfully")
            print(f"  Email/Username: {demo_username}")
            print(f"  Password: {demo_password}")
        
        # Create additional sample users
        print("\n[3/4] Creating sample users...")
        sample_users = [
            {
                "email": "john.doe@tao.com",
                "username": "john.doe",
                "full_name": "John Doe",
                "role": "Developer",
                "password": "password123"
            },
            {
                "email": "jane.smith@tao.com",
                "username": "jane.smith",
                "full_name": "Jane Smith",
                "role": "Product Owner",
                "password": "password123"
            },
            {
                "email": "bob.wilson@tao.com",
                "username": "bob.wilson",
                "full_name": "Bob Wilson",
                "role": "Business Analyst",
                "password": "password123"
            }
        ]
        
        created_users = []
        for user_data in sample_users:
            existing = db.query(User).filter(
                (User.email == user_data["email"]) | (User.username == user_data["username"])
            ).first()
            
            if not existing:
                user = User(
                    email=user_data["email"],
                    username=user_data["username"],
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    hashed_password=get_password_hash(user_data["password"])
                )
                db.add(user)
                created_users.append(user_data["username"])
        
        db.commit()
        
        if created_users:
            print(f"✓ Created {len(created_users)} sample users")
            for username in created_users:
                print(f"  - {username}")
        else:
            print("✓ Sample users already exist")
        
        # Create sample projects
        print("\n[4/4] Creating sample projects...")
        
        demo_user = db.query(User).filter(User.email == demo_username).first()
        
        # Sample projects to create
        sample_projects = [
            {
                "name": "TAO SDLC Demo Project",
                "description": "A comprehensive project management platform with AI-powered SDLC automation, real-time collaboration, and integrated approval workflows.",
                "current_phase": 1,
                "status": "active"
            },
            {
                "name": "E-Commerce Platform Modernization",
                "description": "Modernizing legacy e-commerce platform with microservices architecture, cloud-native deployment, and enhanced user experience.",
                "current_phase": 3,
                "status": "active"
            },
            {
                "name": "Mobile Banking Application",
                "description": "Next-generation mobile banking app with AI-powered financial insights, biometric authentication, and real-time fraud detection.",
                "current_phase": 2,
                "status": "active"
            }
        ]
        
        projects_created = 0
        for project_data in sample_projects:
            existing_project = db.query(Project).filter(
                Project.name == project_data["name"]
            ).first()
            
            if existing_project:
                print(f"✓ Project already exists: {project_data['name']}")
                continue
            
            # Create project
            new_project = Project(
                name=project_data["name"],
                description=project_data["description"],
                current_phase=project_data["current_phase"],
                status=project_data["status"]
            )
            db.add(new_project)
            db.commit()
            db.refresh(new_project)
            
            # Create all phases for the project
            for phase_num, config in PHASE_CONFIGS.items():
                # Set status based on current phase
                if phase_num < project_data["current_phase"]:
                    phase_status = PhaseStatus.APPROVED
                elif phase_num == project_data["current_phase"]:
                    phase_status = PhaseStatus.IN_PROGRESS
                else:
                    phase_status = PhaseStatus.NOT_STARTED
                
                phase = Phase(
                    project_id=new_project.id,
                    phase_number=phase_num,
                    phase_name=config["name"],
                    status=phase_status,
                    data={
                        "description": config["description"],
                        "key_activities": config["key_activities"],
                        "deliverables": config["deliverables"],
                        "approvers": config["approvers"]
                    },
                    ai_confidence_score=0 if phase_status == PhaseStatus.NOT_STARTED else (85 if phase_status == PhaseStatus.APPROVED else 45)
                )
                db.add(phase)
            
            db.commit()
            projects_created += 1
            print(f"✓ Project created: {project_data['name']} (Current Phase: {project_data['current_phase']})")
        
        if projects_created == 0:
            print("✓ All sample projects already exist")
        
        print("\n" + "=" * 60)
        print("Database seed completed successfully! 🎉")
        print("=" * 60)
        print("\nDemo Account Credentials:")
        print(f"  Email/Username: {demo_username}")
        print(f"  Password: {demo_password}")
        print("\nYou can now login using the demo account.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

