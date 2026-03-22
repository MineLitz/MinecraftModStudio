import json
import os
from typing import Optional, List
from core.element import ModElement


class Workspace:
    def __init__(self):
        self.project_name: str = ""
        self.mod_id: str = ""
        self.version: str = "1.0.0"
        self.mc_version: str = "1.21"
        self.loader: str = "NeoForge"
        self.author: str = ""
        self.description: str = ""
        self.elements: List[ModElement] = []
        self.file_path: Optional[str] = None
        self.dirty: bool = False

    def new_project(self, name: str, mod_id: str, mc_version: str,
                    loader: str, author: str = "", description: str = ""):
        self.project_name = name
        self.mod_id = mod_id
        self.mc_version = mc_version
        self.loader = loader
        self.author = author
        self.description = description
        self.elements = []
        self.file_path = None
        self.dirty = False

    def add_element(self, element: ModElement):
        self.elements.append(element)
        self.dirty = True

    def remove_element(self, element_id: str):
        self.elements = [e for e in self.elements if e.id != element_id]
        self.dirty = True

    def get_element(self, element_id: str) -> Optional[ModElement]:
        for e in self.elements:
            if e.id == element_id:
                return e
        return None

    def elements_by_type(self, etype: str) -> List[ModElement]:
        return [e for e in self.elements if e.etype == etype]

    def get_all_types(self) -> List[str]:
        return list({e.etype for e in self.elements})

    def save(self, path: str):
        data = {
            "project_name": self.project_name,
            "mod_id": self.mod_id,
            "version": self.version,
            "mc_version": self.mc_version,
            "loader": self.loader,
            "author": self.author,
            "description": self.description,
            "elements": [e.to_dict() for e in self.elements],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.file_path = path
        self.dirty = False

    def load(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.project_name = data.get("project_name", "")
        self.mod_id = data.get("mod_id", "")
        self.version = data.get("version", "1.0.0")
        self.mc_version = data.get("mc_version", "1.21")
        self.loader = data.get("loader", "NeoForge")
        self.author = data.get("author", "")
        self.description = data.get("description", "")
        self.elements = [ModElement.from_dict(e) for e in data.get("elements", [])]
        self.file_path = path
        self.dirty = False

    def is_empty(self) -> bool:
        return not self.project_name
