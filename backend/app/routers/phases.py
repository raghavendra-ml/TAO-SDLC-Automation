from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter()

@router.get("/project/{project_id}", response_model=List[schemas.Phase])
def get_project_phases(project_id: int, db: Session = Depends(get_db)):
    phases = db.query(models.Phase).filter(
        models.Phase.project_id == project_id
    ).order_by(models.Phase.phase_number).all()
    return phases

@router.get("/{phase_id}", response_model=schemas.Phase)
def get_phase(phase_id: int, db: Session = Depends(get_db)):
    phase = db.query(models.Phase).filter(models.Phase.id == phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    return phase

@router.put("/{phase_id}", response_model=schemas.Phase)
def update_phase(
    phase_id: int,
    phase_update: schemas.PhaseUpdate,
    db: Session = Depends(get_db)
):
    phase = db.query(models.Phase).filter(models.Phase.id == phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    
    # Track if this phase is being approved
    is_being_approved = phase_update.status == models.PhaseStatus.APPROVED and phase.status != models.PhaseStatus.APPROVED
    
    if phase_update.status:
        phase.status = phase_update.status
    if phase_update.data:
        phase.data = phase_update.data
    if phase_update.ai_confidence_score is not None:
        phase.ai_confidence_score = phase_update.ai_confidence_score
    
    # If this phase is being approved, unlock the next phase
    if is_being_approved:
        next_phase = db.query(models.Phase).filter(
            models.Phase.project_id == phase.project_id,
            models.Phase.phase_number == phase.phase_number + 1
        ).first()
        
        if next_phase and next_phase.status == models.PhaseStatus.NOT_STARTED:
            next_phase.status = models.PhaseStatus.IN_PROGRESS
            print(f"✅ Phase {phase.phase_number} approved, unlocking Phase {next_phase.phase_number}")
    
    db.commit()
    db.refresh(phase)
    return phase

