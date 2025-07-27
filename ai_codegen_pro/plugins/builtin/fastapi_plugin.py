"""FastAPI Template Plugin"""

from typing import Dict, List
from ..base import TemplatePlugin, PluginMetadata


class FastAPITemplatePlugin(TemplatePlugin):
    """Plugin für FastAPI-Templates"""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="FastAPI Templates",
            version="1.0.0",
            description="Templates für FastAPI-Anwendungen",
            author="AI CodeGen Pro",
            dependencies=["fastapi", "pydantic", "uvicorn"],
        )

    def initialize(self) -> bool:
        self.logger.info("FastAPI Plugin initialisiert")
        self._initialized = True
        return True

    def cleanup(self) -> None:
        self.logger.info("FastAPI Plugin bereinigt")

    def get_templates(self) -> Dict[str, str]:
        return {
            "fastapi_app.j2": self._get_fastapi_app_template(),
            "fastapi_model.j2": self._get_fastapi_model_template(),
            "fastapi_router.j2": self._get_fastapi_router_template(),
        }

    def get_template_categories(self) -> List[str]:
        return ["FastAPI", "REST API", "Backend"]

    def _get_fastapi_app_template(self) -> str:
        return '''"""
{{ app_name | default('FastAPI Application') }}

{{ description | default('Auto-generated FastAPI application') }}
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="{{ app_name | default('FastAPI Application') }}",
    description="{{ description |
    default('Auto-generated FastAPI application') }}",
    version="{{ version | default('1.0.0') }}"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Hello World",
        "app": "{{ app_name | default('FastAPI Application') }}"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "{{ version | default('1.0.0') }}"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
'''

    def _get_fastapi_model_template(self) -> str:
        return '''"""
{{ model_name | default('Data Model') }} - Pydantic Models

{{ description | default('Auto-generated Pydantic models for FastAPI') }}
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class {{ model_name | default('Item') }}Base(BaseModel):
    """Base model for {{ model_name | default('Item') }}"""
    {% for field_name, field_info in fields.items() %}
    {{ field_name }}: {{ field_info.type | default('str') }}{%
    if field_info.optional %} = None{%
    elif field_info.default is defined %} = {{ field_info.default | repr }}{%
    endif %}
    {% endfor %}

class {{ model_name | default('Item') }}Create(
        {{ model_name | default('Item') }}Base):
    """Model for creating {{ model_name | default('Item') }}"""
    pass

class {{ model_name | default('Item') }}Update(
        {{ model_name | default('Item') }}Base):
    """Model for updating {{ model_name | default('Item') }}"""
    {% for field_name in fields.keys() %}
    {{ field_name }}: Optional[{{ fields[field_name].type |
    default('str') }}] = None
    {% endfor %}

class {{ model_name | default('Item') }}Response(
        {{ model_name | default('Item') }}Base):
    """Model for {{ model_name | default('Item') }} response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
'''

    def _get_fastapi_router_template(self) -> str:
        return '''"""
{{ router_name | default('Router') }} - FastAPI Router

{{ description | default('Auto-generated FastAPI router') }}
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

router = APIRouter()

@router.get("/")
async def list_{{ resource_name | default('items') }}():
    """List all {{ resource_name | default('items') }}"""
    return {"message": "List {{ resource_name | default('items') }}"}

@router.get("/{item_id}")
async def get_{{ resource_name | default('item') }}(item_id: int):
    """Get {{ resource_name | default('item') }} by ID"""
    return {
        "id": item_id,
        "message": "Get {{ resource_name | default('item') }}"
    }

@router.post("/")
async def create_{{ resource_name | default('item') }}():
    """Create new {{ resource_name | default('item') }}"""
    return {"message": "Create {{ resource_name | default('item') }}"}

@router.put("/{item_id}")
async def update_{{ resource_name | default('item') }}(item_id: int):
    """Update {{ resource_name | default('item') }}"""
    return {
        "id": item_id,
        "message": "Update {{ resource_name | default('item') }}"
    }

@router.delete("/{item_id}")
async def delete_{{ resource_name | default('item') }}(item_id: int):
    """Delete {{ resource_name | default('item') }}"""
    return {
        "id": item_id,
        "message": "Delete {{ resource_name | default('item') }}"
    }
'''
