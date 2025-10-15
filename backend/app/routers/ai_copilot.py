from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app import models, schemas
from app.database import get_db
from app.services.ai_service import AIService
from app.services.document_parser import DocumentParser
import tempfile
import os

router = APIRouter()
ai_service = AIService()
doc_parser = DocumentParser()

@router.post("/query", response_model=schemas.AIResponse)
async def ai_query(query: schemas.AIQuery, db: Session = Depends(get_db)):
    """
    Process AI query for a specific project phase
    """
    try:
        # Get phase context
        phase = db.query(models.Phase).filter(models.Phase.id == query.phase_id).first()
        if not phase:
            raise HTTPException(status_code=404, detail="Phase not found")
        
        # Process with AI service
        response = await ai_service.process_query(
            query.query,
            phase.phase_name,
            query.context
        )
        
        # Store interaction
        interaction = models.AIInteraction(
            project_id=query.project_id,
            phase_id=query.phase_id,
            user_query=query.query,
            ai_response=response["response"],
            confidence_score=response["confidence_score"]
        )
        db.add(interaction)
        db.commit()
        
        return schemas.AIResponse(
            response=response["response"],
            confidence_score=response["confidence_score"],
            alternatives=response.get("alternatives", []),
            explanation=response.get("explanation")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/{phase_id}")
async def generate_content(
    phase_id: int,
    request_data: dict,
    db: Session = Depends(get_db)
):
    """
    Generate phase-specific content (PRD, FSD, Architecture, etc.)
    """
    phase = db.query(models.Phase).filter(models.Phase.id == phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    
    content_type = request_data.get("content_type")
    if not content_type:
        raise HTTPException(status_code=400, detail="content_type is required")
    
    # Use the data from request (fresh requirements) instead of cached phase data
    generation_data = {
        "requirements": request_data.get("requirements", []),
        "gherkinRequirements": request_data.get("gherkinRequirements", []),
        "prd": request_data.get("prd"),
        "brd": request_data.get("brd"),
        "epics": request_data.get("epics", []),
        "project": request_data.get("project")
    }
    
    result = await ai_service.generate_content(phase.phase_name, content_type, generation_data)
    return result

@router.post("/extract-requirements")
async def extract_requirements(
    files: List[UploadFile] = File(...),
    project_id: int = Form(...),
    phase_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Extract requirements from uploaded documents and convert to Gherkin format using OpenAI.
    
    Returns:
        - requirements: List of Gherkin format requirements
        - count: Number of requirements extracted
    """
    try:
        # Get project info
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        project_name = project.name if project else "Project"
        
        all_requirements = []
        
        print(f"[INFO] Extracting requirements from {len(files)} file(s) for project: {project_name}")
        
        for file in files:
            print(f"[INFO] Processing file: {file.filename}")
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            try:
                # Parse document
                print(f"[INFO] Parsing document: {file.filename}")
                parsed_content = doc_parser.parse_document(tmp_path, file.filename)
                
                # Extract and convert to Gherkin format using OpenAI
                print(f"[INFO] Extracting requirements with OpenAI from: {file.filename}")
                gherkin_requirements = await ai_service.convert_to_gherkin(parsed_content)
                
                print(f"[OK] Extracted {len(gherkin_requirements)} requirements from {file.filename}")
                all_requirements.extend(gherkin_requirements)
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        if not all_requirements:
            return {
                "status": "warning",
                "requirements": [],
                "count": 0,
                "message": "No requirements could be extracted from the uploaded documents. Please check the document format and content."
            }
        
        print(f"[SUCCESS] Extraction complete: {len(all_requirements)} requirements extracted")
        
        return {
            "status": "success",
            "requirements": all_requirements,
            "count": len(all_requirements),
            "message": f"Successfully extracted {len(all_requirements)} requirements. You can now generate PRD and BRD."
        }
    except Exception as e:
        print(f"[ERROR] Failed to extract requirements: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to extract requirements: {str(e)}")

@router.post("/analyze-risks/{phase_id}")
async def analyze_risks(
    phase_id: int,
    db: Session = Depends(get_db)
):
    """
    Analyze risks based on extracted requirements using AI.
    
    Returns:
        - risks: List of risk assessments with priority, impact, and mitigation
        - count: Number of risks identified
    """
    try:
        # Get phase and verify it's Requirements phase
        phase = db.query(models.Phase).filter(models.Phase.id == phase_id).first()
        if not phase:
            raise HTTPException(status_code=404, detail="Phase not found")
        
        # Get project info
        project = db.query(models.Project).filter(models.Project.id == phase.project_id).first()
        project_name = project.name if project else "Project"
        
        # Get requirements from phase data
        phase_data = phase.data or {}
        requirements = phase_data.get('gherkinRequirements', [])
        
        if not requirements:
            # Try legacy format
            requirements = phase_data.get('requirements', [])
        
        if not requirements:
            return {
                "status": "warning",
                "risks": [],
                "count": 0,
                "message": "No requirements found. Please extract requirements first."
            }
        
        print(f"[INFO] Analyzing risks for {len(requirements)} requirements in project: {project_name}")
        
        # Analyze risks using OpenAI
        risks = await ai_service.analyze_risks(requirements, project_name)
        
        # Store risks in phase data
        phase_data['risks'] = risks
        phase.data = phase_data
        phase.updated_at = datetime.utcnow()
        db.commit()
        
        print(f"[SUCCESS] Risk analysis complete: {len(risks)} risks identified")
        
        return {
            "status": "success",
            "risks": risks,
            "count": len(risks),
            "message": f"Successfully identified {len(risks)} risks with mitigation strategies."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to analyze risks: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to analyze risks: {str(e)}")

