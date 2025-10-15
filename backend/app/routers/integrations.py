from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app import models
from app.models_integrations import IntegrationConfig, IntegrationLog
from app.database import get_db
from app.services.integration_service import IntegrationService

router = APIRouter()
integration_service = IntegrationService()

@router.post("/jira/connect")
async def connect_jira(
    project_id: int,
    jira_config: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Connect Jira to a project
    Config should include: url, email, api_token, project_key
    """
    try:
        # Test connection
        result = await integration_service.test_jira_connection(jira_config)
        
        if result["success"]:
            # Save configuration
            config = IntegrationConfig(
                project_id=project_id,
                integration_type="jira",
                config=jira_config,
                is_active=True
            )
            db.add(config)
            db.commit()
            
            # Log the integration
            log = IntegrationLog(
                project_id=project_id,
                integration_type="jira",
                action="connect",
                status="success",
                request_data={"project_id": project_id},
                response_data=result
            )
            db.add(log)
            db.commit()
            
            return {"message": "Jira connected successfully", "data": result}
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Connection failed"))
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jira/sync-epics/{project_id}")
async def sync_jira_epics(
    project_id: int,
    phase_id: int,
    db: Session = Depends(get_db)
):
    """
    Sync epics from TAO SDLC to Jira
    """
    try:
        # Get integration config
        config = db.query(IntegrationConfig).filter(
            IntegrationConfig.project_id == project_id,
            IntegrationConfig.integration_type == "jira",
            IntegrationConfig.is_active == True
        ).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="Jira integration not configured")
        
        # Get phase data
        phase = db.query(models.Phase).filter(models.Phase.id == phase_id).first()
        if not phase:
            raise HTTPException(status_code=404, detail="Phase not found")
        
        # Sync epics
        result = await integration_service.sync_epics_to_jira(config.config, phase.data)
        
        # Log the action
        log = IntegrationLog(
            project_id=project_id,
            integration_type="jira",
            action="sync_epics",
            status="success" if result["success"] else "failed",
            request_data={"phase_id": phase_id},
            response_data=result
        )
        db.add(log)
        db.commit()
        
        return result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/github/connect")
async def connect_github(
    project_id: int,
    github_config: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Connect GitHub to a project
    Config should include: token, owner, repo
    """
    try:
        # Test connection
        result = await integration_service.test_github_connection(github_config)
        
        if result["success"]:
            config = IntegrationConfig(
                project_id=project_id,
                integration_type="github",
                config=github_config,
                is_active=True
            )
            db.add(config)
            db.commit()
            
            log = IntegrationLog(
                project_id=project_id,
                integration_type="github",
                action="connect",
                status="success",
                request_data={"project_id": project_id},
                response_data=result
            )
            db.add(log)
            db.commit()
            
            return {"message": "GitHub connected successfully", "data": result}
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Connection failed"))
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/github/create-repo/{project_id}")
async def create_github_repo(
    project_id: int,
    repo_config: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Create GitHub repository for the project
    """
    try:
        config = db.query(IntegrationConfig).filter(
            IntegrationConfig.project_id == project_id,
            IntegrationConfig.integration_type == "github",
            IntegrationConfig.is_active == True
        ).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="GitHub integration not configured")
        
        result = await integration_service.create_github_repo(config.config, repo_config)
        
        log = IntegrationLog(
            project_id=project_id,
            integration_type="github",
            action="create_repo",
            status="success" if result["success"] else "failed",
            request_data=repo_config,
            response_data=result
        )
        db.add(log)
        db.commit()
        
        return result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confluence/connect")
async def connect_confluence(
    project_id: int,
    confluence_config: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Connect Confluence to a project
    Config should include: url, email, api_token, space_key
    """
    try:
        result = await integration_service.test_confluence_connection(confluence_config)
        
        if result["success"]:
            config = IntegrationConfig(
                project_id=project_id,
                integration_type="confluence",
                config=confluence_config,
                is_active=True
            )
            db.add(config)
            db.commit()
            
            return {"message": "Confluence connected successfully", "data": result}
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Connection failed"))
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confluence/publish/{project_id}")
async def publish_to_confluence(
    project_id: int,
    content: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Publish documentation to Confluence
    """
    try:
        config = db.query(IntegrationConfig).filter(
            IntegrationConfig.project_id == project_id,
            IntegrationConfig.integration_type == "confluence",
            IntegrationConfig.is_active == True
        ).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="Confluence integration not configured")
        
        result = await integration_service.publish_to_confluence(config.config, content)
        
        log = IntegrationLog(
            project_id=project_id,
            integration_type="confluence",
            action="publish_documentation",
            status="success" if result["success"] else "failed",
            request_data=content,
            response_data=result
        )
        db.add(log)
        db.commit()
        
        return result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/{project_id}")
def get_integration_logs(
    project_id: int,
    integration_type: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get integration logs for a project
    """
    query = db.query(IntegrationLog).filter(IntegrationLog.project_id == project_id)
    
    if integration_type:
        query = query.filter(IntegrationLog.integration_type == integration_type)
    
    logs = query.order_by(IntegrationLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs

@router.get("/config/{project_id}")
def get_integrations(project_id: int, db: Session = Depends(get_db)):
    """
    Get all integration configurations for a project
    """
    configs = db.query(IntegrationConfig).filter(
        IntegrationConfig.project_id == project_id
    ).all()
    return configs

@router.delete("/config/{config_id}")
def delete_integration(config_id: int, db: Session = Depends(get_db)):
    """
    Delete an integration configuration
    """
    config = db.query(IntegrationConfig).filter(IntegrationConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Integration configuration not found")
    
    db.delete(config)
    db.commit()
    return {"message": "Integration deleted successfully"}

