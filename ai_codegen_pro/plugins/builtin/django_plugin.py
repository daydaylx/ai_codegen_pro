"""Django Template Plugin"""

from typing import Dict, List
from ..base import TemplatePlugin, PluginMetadata


class DjangoTemplatePlugin(TemplatePlugin):
    """Plugin für Django-Templates"""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Django Templates",
            version="1.0.0",
            description="Templates für Django-Anwendungen",
            author="AI CodeGen Pro",
            dependencies=["django", "djangorestframework"],
        )

    def initialize(self) -> bool:
        self.logger.info("Django Plugin initialisiert")
        self._initialized = True
        return True

    def cleanup(self) -> None:
        self.logger.info("Django Plugin bereinigt")

    def get_templates(self) -> Dict[str, str]:
        return {
            "django_model.j2": self._get_django_model_template(),
            "django_view.j2": self._get_django_view_template(),
            "django_serializer.j2": self._get_django_serializer_template(),
        }

    def get_template_categories(self) -> List[str]:
        return ["Django", "Web Framework", "Backend"]

    def _get_django_model_template(self) -> str:
        return '''"""
{{ model_name | default('Model') }} - Django Model

{{ description | default('Auto-generated Django model') }}
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class {{ model_name | default('Model') }}(models.Model):
    """{{ description | default('Django model for ' +
    (model_name | default('Model'))) }}"""

    {% for field_name, field_info in fields.items() %}
    {{ field_name }} = models.{{ field_info.type | default('CharField') }}(
        {% if field_info.max_length %}max_length={{ field_info.max_length }},{% endif %}
        {% if field_info.help_text %}help_text="{{ field_info.help_text }}",{% endif %}
        {% if field_info.blank %}blank={{ field_info.blank }},{% endif %}
        {% if field_info.null %}null={{ field_info.null }},{% endif %}
    )
    {% endfor %}

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "{{ verbose_name | default(model_name |
        default('Item')) }}"
        verbose_name_plural = "{{ verbose_name_plural |
        default((model_name | default('Items')) + 's') }}"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{{ model_name | default('Model') }} #{self.pk}"
'''

    def _get_django_view_template(self) -> str:
        return '''"""
{{ view_name | default('View') }} - Django Views

{{ description | default('Auto-generated Django views') }}
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import {{ model_name | default('Model') }}

def {{ model_name.lower() | default('item') }}_list(request):
    """List all {{ model_name.lower() | default('items') }}"""
    items = {{ model_name | default('Model') }}.objects.all()

    paginator = Paginator(items, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': '{{ model_name | default('Items') }} Liste'
    }
    return render(request,
                  'app/{{ model_name.lower() |
                  default('item') }}_list.html', context)

def {{ model_name.lower() | default('item') }}_detail(request, pk):
    """Detail view for {{ model_name.lower() | default('item') }}"""
    item = get_object_or_404({{ model_name | default('Model') }}, pk=pk)

    context = {
        'item': item,
        'title': f'{{ model_name | default('Item') }} #{item.pk}'
    }
    return render(request,
                  'app/{{ model_name.lower() |
                  default('item') }}_detail.html', context)
'''

    def _get_django_serializer_template(self) -> str:
        return '''"""
{{ model_name | default('Model') }} Serializers for Django REST Framework

{{ description | default('Auto-generated Django REST Framework serializers') }}
"""

from rest_framework import serializers
from .models import {{ model_name | default('Model') }}

class {{ model_name | default('Model') }}Serializer(serializers.ModelSerializer):
    """Serializer for {{ model_name | default('Model') }}"""

    class Meta:
        model = {{ model_name | default('Model') }}
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class {{ model_name | default('Model') }}CreateSerializer(
        serializers.ModelSerializer):
    """Serializer for creating {{ model_name | default('Model') }}"""

    class Meta:
        model = {{ model_name | default('Model') }}
        exclude = ['created_at', 'updated_at']
'''
