"""
Tool Registry - Defines tools and their schemas for Voice Live function calling.
"""

from typing import Callable, Dict, Any
import json


class ToolRegistry:
    """Manages tools that the voice agent can call."""

    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: list = []

    def register(self, name: str, description: str, parameters: dict):
        """Decorator to register a tool with its schema."""
        
        def decorator(func: Callable):
            self.tools[name] = func
            # Voice Live API expects flat structure, not nested under "function"
            self.schemas.append({
                "type": "function",
                "name": name,
                "description": description,
                "parameters": parameters
            })
            return func
        
        return decorator

    def execute(self, name: str, arguments: dict) -> str:
        """Execute a tool by name with given arguments."""
        
        if name not in self.tools:
            return json.dumps({"error": f"Tool '{name}' not found"})
        
        try:
            result = self.tools[name](**arguments)
            return json.dumps(result) if isinstance(result, dict) else str(result)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_schemas(self) -> list:
        """Get all tool schemas for Voice Live session config."""
        return self.schemas


# Global registry instance
registry = ToolRegistry()


# Note: Onboarding tools (B.1-B.5) are registered in onboarding_tools.py
# which is imported via tools/__init__.py
