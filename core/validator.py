from dataclasses import dataclass
from typing import List
from core.workspace import Workspace


@dataclass
class ValidationIssue:
    level: str   # "error" | "warning" | "info"
    element_name: str
    message: str

    @property
    def icon(self):
        return {"error": "✖", "warning": "⚠", "info": "ℹ"}.get(self.level, "•")

    @property
    def color(self):
        return {"error": "#c04040", "warning": "#c89040", "info": "#4888c8"}.get(self.level, "#888")


class ModValidator:
    def __init__(self, workspace: Workspace):
        self.ws = workspace

    def validate(self) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        if not self.ws.project_name:
            issues.append(ValidationIssue("error", "Projeto", "Nenhum projeto aberto."))
            return issues

        if not self.ws.elements:
            issues.append(ValidationIssue("warning", "Projeto", "O mod não tem nenhum elemento criado."))
            return issues

        # Check duplicate registry names
        registry_names = [e.registry_name for e in self.ws.elements]
        seen = set()
        for e in self.ws.elements:
            if e.registry_name in seen:
                issues.append(ValidationIssue(
                    "error", e.name,
                    f"ID duplicado: '{e.registry_name}' já existe em outro elemento."
                ))
            seen.add(e.registry_name)

        # Check empty registry names
        for e in self.ws.elements:
            if not e.registry_name.strip():
                issues.append(ValidationIssue("error", e.name, "Registry ID está vazio."))

        # Check registry name format (lowercase, no spaces)
        for e in self.ws.elements:
            rn = e.registry_name
            if rn and (rn != rn.lower() or " " in rn):
                issues.append(ValidationIssue(
                    "warning", e.name,
                    f"Registry ID '{rn}' deve ser minúsculo e sem espaços."
                ))

        # Type-specific checks
        for e in self.ws.elements:
            p = e.props
            if e.etype == "item":
                if p.get("damage", 0) < 0:
                    issues.append(ValidationIssue("error", e.name, "Dano não pode ser negativo."))
                if p.get("durability", 0) < 0:
                    issues.append(ValidationIssue("error", e.name, "Durabilidade não pode ser negativa."))
                if p.get("max_stack", 64) < 1:
                    issues.append(ValidationIssue("error", e.name, "Stack máximo deve ser pelo menos 1."))
                if p.get("food") and p.get("food_nutrition", 0) == 0:
                    issues.append(ValidationIssue("warning", e.name, "Item marcado como comida mas nutrição é 0."))

            elif e.etype == "block":
                if p.get("hardness", 1.5) < -1:
                    issues.append(ValidationIssue("error", e.name, "Dureza inválida (mínimo -1 para inquebrável)."))
                if p.get("luminance", 0) > 15:
                    issues.append(ValidationIssue("error", e.name, "Luminosidade máxima é 15."))

            elif e.etype == "mob":
                if p.get("hp", 20) <= 0:
                    issues.append(ValidationIssue("error", e.name, "HP deve ser maior que 0."))
                if p.get("speed", 0.35) < 0:
                    issues.append(ValidationIssue("error", e.name, "Velocidade não pode ser negativa."))
                if p.get("damage", 3) < 0:
                    issues.append(ValidationIssue("error", e.name, "Dano não pode ser negativo."))

            elif e.etype == "recipe":
                if not p.get("result_item", "").strip():
                    issues.append(ValidationIssue("warning", e.name, "Receita sem item resultado definido."))

            elif e.etype == "enchant":
                if p.get("max_level", 1) < 1:
                    issues.append(ValidationIssue("error", e.name, "Nível máximo deve ser pelo menos 1."))

        # Mod ID check
        mid = self.ws.mod_id
        if not mid:
            issues.append(ValidationIssue("error", "Projeto", "Mod ID está vazio."))
        elif mid != mid.lower() or " " in mid:
            issues.append(ValidationIssue("warning", "Projeto", "Mod ID deve ser minúsculo e sem espaços."))

        if not issues:
            issues.append(ValidationIssue("info", "Projeto", "Nenhum problema encontrado. Mod pronto para build!"))

        return issues
