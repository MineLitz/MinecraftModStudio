# ⛏ Minecraft Mod Studio

Criador visual de mods para **Minecraft Java Edition** — sem precisar escrever código.

---

## 🚀 Como Executar (Windows)

### 1. Instalar Python
Baixe e instale o Python 3.11+ em: https://www.python.org/downloads/

> ⚠️ **IMPORTANTE:** Durante a instalação, marque a opção **"Add Python to PATH"**

### 2. Instalar Dependências
Dê duplo clique em `install.bat`

### 3. Executar o App
Dê duplo clique em `run.bat`

---

## 📋 Requisitos

| Requisito     | Versão Mínima |
|---------------|---------------|
| Python        | 3.11+         |
| PyQt6         | 6.6.0+        |
| Windows       | 10 / 11       |
| RAM           | 256 MB+       |

---

## 🎮 Funcionalidades

- **Tela de boas-vindas** com projetos recentes
- **Workspace visual** — cards para cada elemento do mod
- **8 tipos de elementos:** Itens, Blocos, Mobs, Receitas, Biomas, Encantos, Poções, Comandos
- **Painel de propriedades** — edite tudo visualmente
- **Sidebar com árvore** de elementos e busca
- **Console integrado** com feedback em tempo real
- **Exportação** da estrutura completa do mod (ZIP)
- **Salvar/Abrir projetos** no formato `.mms`
- **Sistema de plugins** (pasta `plugins/`)

---

## 📁 Estrutura do Projeto

```
MinecraftModStudio/
├── main.py                 ← Ponto de entrada
├── requirements.txt        ← Dependências Python
├── install.bat             ← Instalar dependências (Windows)
├── run.bat                 ← Executar o app (Windows)
├── core/
│   ├── element.py          ← Modelo de dados dos elementos
│   ├── workspace.py        ← Gerenciamento do projeto
│   └── exporter.py         ← Exportação do mod
├── ui/
│   ├── theme.py            ← Tema escuro (QSS)
│   ├── welcome_screen.py   ← Tela de boas-vindas
│   ├── mainwindow.py       ← Janela principal
│   ├── workspace_panel.py  ← Cards dos elementos
│   ├── properties_panel.py ← Painel de propriedades
│   └── dialogs/
│       ├── new_project_dialog.py
│       └── new_element_dialog.py
└── plugins/                ← Pasta para plugins externos
```

---

## 🔌 Sistema de Plugins

Coloque arquivos `.py` na pasta `plugins/` para adicionar funcionalidades.
*(em desenvolvimento)*

---

## ⌨️ Atalhos de Teclado

| Atalho         | Ação                    |
|----------------|-------------------------|
| `Ctrl+N`       | Novo Projeto            |
| `Ctrl+O`       | Abrir Projeto           |
| `Ctrl+S`       | Salvar                  |
| `Ctrl+E`       | Novo Elemento           |
| `Ctrl+B`       | Build do Mod            |
| `Ctrl+Shift+E` | Exportar Estrutura      |

---

## ⚠️ Aviso

Este é um projeto não oficial. Não possui afiliação com Mojang ou Microsoft.
Minecraft® é marca registrada da Mojang Studios.

---

*Desenvolvido com ❤️ usando Python + PyQt6*
