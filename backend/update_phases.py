"""
Update existing projects to have all phases
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import Project, Phase, PhaseStatus, PHASE_CONFIGS
from app import models_integrations

def update_project_phases():
    """Add missing phases to existing projects"""
    print("=" * 60)
    print("Updating Project Phases")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Get all projects
        projects = db.query(Project).all()
        print(f"\nFound {len(projects)} projects")
        
        for project in projects:
            print(f"\n📦 Processing: {project.name}")
            
            # Get existing phases for this project
            existing_phases = db.query(Phase).filter(
                Phase.project_id == project.id
            ).all()
            
            existing_phase_numbers = {p.phase_number for p in existing_phases}
            print(f"  Existing phases: {sorted(existing_phase_numbers)}")
            
            # Add missing phases
            phases_added = []
            for phase_num, config in PHASE_CONFIGS.items():
                if phase_num not in existing_phase_numbers:
                    # Determine status based on current phase
                    if phase_num < project.current_phase:
                        phase_status = PhaseStatus.APPROVED
                    elif phase_num == project.current_phase:
                        phase_status = PhaseStatus.IN_PROGRESS
                    else:
                        phase_status = PhaseStatus.NOT_STARTED
                    
                    phase = Phase(
                        project_id=project.id,
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
                    phases_added.append(phase_num)
            
            if phases_added:
                db.commit()
                print(f"  ✓ Added phases: {sorted(phases_added)}")
            else:
                print(f"  ✓ All phases already exist")
        
        print("\n" + "=" * 60)
        print("Phase update completed! 🎉")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_project_phases()

