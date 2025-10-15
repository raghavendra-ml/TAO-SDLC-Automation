import httpx
from typing import Dict, Any, List
import json

class IntegrationService:
    """
    Service for handling third-party integrations
    """
    
    async def test_jira_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test Jira connection
        """
        try:
            url = config.get("url")
            email = config.get("email")
            api_token = config.get("api_token")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{url}/rest/api/3/myself",
                    auth=(email, api_token),
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "success": True,
                        "message": "Connected to Jira successfully",
                        "user": user_data.get("displayName")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to connect: {response.status_code}"
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def sync_epics_to_jira(self, config: Dict[str, Any], phase_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync epics from TAO SDLC to Jira
        """
        try:
            url = config.get("url")
            email = config.get("email")
            api_token = config.get("api_token")
            project_key = config.get("project_key")
            
            epics = phase_data.get("epics", [])
            created_epics = []
            
            async with httpx.AsyncClient() as client:
                for epic in epics:
                    # Create epic in Jira
                    epic_data = {
                        "fields": {
                            "project": {"key": project_key},
                            "summary": epic.get("title", ""),
                            "description": epic.get("description", ""),
                            "issuetype": {"name": "Epic"}
                        }
                    }
                    
                    response = await client.post(
                        f"{url}/rest/api/3/issue",
                        auth=(email, api_token),
                        json=epic_data,
                        timeout=10.0
                    )
                    
                    if response.status_code == 201:
                        created_epic = response.json()
                        created_epics.append({
                            "key": created_epic.get("key"),
                            "id": created_epic.get("id"),
                            "title": epic.get("title")
                        })
            
            return {
                "success": True,
                "message": f"Created {len(created_epics)} epics in Jira",
                "epics": created_epics
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_github_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test GitHub connection
        """
        try:
            token = config.get("token")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"token {token}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "success": True,
                        "message": "Connected to GitHub successfully",
                        "user": user_data.get("login")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to connect: {response.status_code}"
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_github_repo(self, config: Dict[str, Any], repo_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a GitHub repository
        """
        try:
            token = config.get("token")
            owner = config.get("owner")
            
            repo_data = {
                "name": repo_config.get("name"),
                "description": repo_config.get("description", ""),
                "private": repo_config.get("private", True),
                "auto_init": True
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.github.com/user/repos",
                    headers={"Authorization": f"token {token}"},
                    json=repo_data,
                    timeout=10.0
                )
                
                if response.status_code == 201:
                    repo = response.json()
                    return {
                        "success": True,
                        "message": "Repository created successfully",
                        "repo_url": repo.get("html_url"),
                        "clone_url": repo.get("clone_url")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to create repository: {response.status_code}"
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_confluence_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test Confluence connection
        """
        try:
            url = config.get("url")
            email = config.get("email")
            api_token = config.get("api_token")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{url}/wiki/rest/api/user/current",
                    auth=(email, api_token),
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "success": True,
                        "message": "Connected to Confluence successfully",
                        "user": user_data.get("displayName")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to connect: {response.status_code}"
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def publish_to_confluence(self, config: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish documentation to Confluence
        """
        try:
            url = config.get("url")
            email = config.get("email")
            api_token = config.get("api_token")
            space_key = config.get("space_key")
            
            page_data = {
                "type": "page",
                "title": content.get("title"),
                "space": {"key": space_key},
                "body": {
                    "storage": {
                        "value": content.get("body"),
                        "representation": "storage"
                    }
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{url}/wiki/rest/api/content",
                    auth=(email, api_token),
                    json=page_data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    page = response.json()
                    return {
                        "success": True,
                        "message": "Page published successfully",
                        "page_url": f"{url}/wiki{page.get('_links', {}).get('webui')}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to publish: {response.status_code}"
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}

