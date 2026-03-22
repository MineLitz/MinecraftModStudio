# Pasta de Plugins

Coloque seus plugins `.py` aqui para adicionar funcionalidades ao Minecraft Mod Studio.

## Como criar um plugin

Crie um arquivo `.py` nesta pasta com o seguinte formato:

```python
# meu_plugin.py

PLUGIN_NAME = "Meu Plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "Seu Nome"

def on_load(app):
    """Chamado quando o plugin é carregado."""
    print(f"{PLUGIN_NAME} carregado!")

def on_element_created(element):
    """Chamado quando um novo elemento é criado."""
    pass
```
