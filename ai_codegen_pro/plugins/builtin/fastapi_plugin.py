"""FastAPI Plugin für AI CodeGen Pro"""

from typing import Any, Dict, List

from ...core.template_service import TemplateService
from ...utils.logger_service import LoggerService
from ..base import BasePlugin


class FastAPIPlugin(BasePlugin):
    """Plugin für FastAPI-spezifische Codegenerierung"""

    def __init__(self):
        super().__init__()
        self.name = "FastAPI Plugin"
        self.version = "1.0.0"
        self.description = "FastAPI API, Models, Router Generator"
        self.author = "AI CodeGen Pro"
        self.logger = LoggerService().get_logger(__name__)
        self.template_service = TemplateService()

    def initialize(self) -> bool:
        """Plugin initialisieren"""
        try:
            self._register_templates()
            return True
        except Exception as e:
            self.logger.error(f"FastAPI Plugin init failed: {e}")
            return False

    def _register_templates(self):
        """FastAPI-Templates registrieren"""
        templates = {
            "fastapi_main": self._get_main_template(),
            "fastapi_model": self._get_model_template(),
            "fastapi_router": self._get_router_template(),
            "fastapi_crud": self._get_crud_template(),
        }

        for name, template in templates.items():
            self.template_service.register_template(name, template)

    def generate_main_app(self, app_name: str, **kwargs) -> str:
        """FastAPI Main App generieren"""
        template_vars = {
            "app_name": app_name,
            "description": kwargs.get("description", f"{app_name} API"),
            "version": kwargs.get("version", "1.0.0"),
            "routers": kwargs.get("routers", []),
        }

        return self.template_service.render_template("fastapi_main", template_vars)

    def generate_pydantic_model(self, model_name: str, fields: Dict[str, str], **kwargs) -> str:
        """Pydantic Model generieren"""
        template_vars = {
            "model_name": model_name,
            "fields": fields,
            "base_model": kwargs.get("base_model", "BaseModel"),
            "config": kwargs.get("config", {}),
        }

        return self.template_service.render_template("fastapi_model", template_vars)

    def generate_router(self, router_name: str, endpoints: List[Dict], **kwargs) -> str:
        """FastAPI Router generieren"""
        template_vars = {
            "router_name": router_name,
            "endpoints": endpoints,
            "prefix": kwargs.get("prefix", f"/{router_name.lower()}"),
            "tags": kwargs.get("tags", [router_name]),
        }

        return self.template_service.render_template("fastapi_router", template_vars)

    def _get_main_template(self) -> str:
        """FastAPI Main App Template"""
        return '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="{{ app_name }}",
    description="{{ description }}",
    version="{{ version }}"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

{% for router in routers %}
from .routers import {{ router }}
app.include_router({{ router }}.router)
{% endfor %}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "{{ app_name }} API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
'''

    def _get_model_template(self) -> str:
        """Pydantic Model Template"""
        return '''from pydantic import {{ base_model }}, Field
from typing import Optional
from datetime import datetime

class {{ model_name }}({{ base_model }}):
    """{{ model_name }} Pydantic Model"""

    {% for field_name, field_type in fields.items() %}
    {{ field_name }}: {{ field_type }}
    {% endfor %}

    class Config:
        {% for key, value in config.items() %}
        {{ key }} = {{ value }}
        {% endfor %}

class {{ model_name }}Create({{ base_model }}):
    """{{ model_name }} Create Schema"""
    {% for field_name, field_type in fields.items() %}
    {{ field_name }}: {{ field_type }}
    {% endfor %}

class {{ model_name }}Update({{ base_model }}):
    """{{ model_name }} Update Schema"""
    {% for field_name, field_type in fields.items() %}
    {{ field_name }}: Optional[{{ field_type }}] = None
    {% endfor %}
'''

    def _get_router_template(self) -> str:
        """FastAPI Router Template"""
        return '''from fastapi import APIRouter, HTTPException, Depends
from typing import List

router = APIRouter(
    prefix="{{ prefix }}",
    tags={{ tags }}
)

{% for endpoint in endpoints %}
@router.{{ endpoint.method }}("{{ endpoint.path }}")
async def {{ endpoint.name }}():
    """{{ endpoint.description or endpoint.name }}"""
    return {"message": "{{ endpoint.name }} endpoint"}

{% endfor %}
'''

    def _get_crud_template(self) -> str:
        """FastAPI CRUD Template"""
        return '''from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/", response_model={{ model_name }})
async def create_{{ model_name|lower }}(
    item: {{ model_name }}Create,
    db: Session = Depends(get_db)
):
    """Create new {{ model_name }}"""
    return crud.create_{{ model_name|lower }}(db=db, item=item)

@router.get("/", response_model=List[{{ model_name }}])
async def read_{{ model_name|lower }}s(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all {{ model_name }}s"""
    items = crud.get_{{ model_name|lower }}s(db, skip=skip, limit=limit)
    return items

@router.get("/{item_id}", response_model={{ model_name }})
async def read_{{ model_name|lower }}(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Get {{ model_name }} by ID"""
    item = crud.get_{{ model_name|lower }}(db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
'''

    def get_capabilities(self) -> Dict[str, Any]:
        """Plugin-Fähigkeiten zurückgeben"""
        return {
            "templates": ["fastapi_main", "fastapi_model", "fastapi_router"],
            "generators": ["main_app", "pydantic_model", "router", "crud"],
            "framework": "fastapi",
            "languages": ["python"],
        }
