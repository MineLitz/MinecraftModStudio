import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QHeaderView, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

# All translatable MC keys organized by type
LANG_ENTRIES = {
    "Blocos": [
        ("block.minecraft.stone",            "Stone",              "Pedra"),
        ("block.minecraft.granite",          "Granite",            "Granito"),
        ("block.minecraft.diorite",          "Diorite",            "Diorito"),
        ("block.minecraft.andesite",         "Andesite",           "Andesito"),
        ("block.minecraft.grass_block",      "Grass Block",        "Bloco de Grama"),
        ("block.minecraft.dirt",             "Dirt",               "Terra"),
        ("block.minecraft.cobblestone",      "Cobblestone",        "Paralelepípedo"),
        ("block.minecraft.oak_planks",       "Oak Planks",         "Prancha de Carvalho"),
        ("block.minecraft.spruce_planks",    "Spruce Planks",      "Prancha de Pinheiro"),
        ("block.minecraft.birch_planks",     "Birch Planks",       "Prancha de Bétula"),
        ("block.minecraft.sand",             "Sand",               "Areia"),
        ("block.minecraft.gravel",           "Gravel",             "Cascalho"),
        ("block.minecraft.gold_ore",         "Gold Ore",           "Minério de Ouro"),
        ("block.minecraft.iron_ore",         "Iron Ore",           "Minério de Ferro"),
        ("block.minecraft.coal_ore",         "Coal Ore",           "Minério de Carvão"),
        ("block.minecraft.diamond_ore",      "Diamond Ore",        "Minério de Diamante"),
        ("block.minecraft.obsidian",         "Obsidian",           "Obsidiana"),
        ("block.minecraft.tnt",              "TNT",                "TNT"),
        ("block.minecraft.bookshelf",        "Bookshelf",          "Estante de Livros"),
        ("block.minecraft.glass",            "Glass",              "Vidro"),
        ("block.minecraft.gold_block",       "Block of Gold",      "Bloco de Ouro"),
        ("block.minecraft.iron_block",       "Block of Iron",      "Bloco de Ferro"),
        ("block.minecraft.diamond_block",    "Block of Diamond",   "Bloco de Diamante"),
        ("block.minecraft.bricks",           "Bricks",             "Tijolos"),
        ("block.minecraft.netherrack",       "Netherrack",         "Netherrack"),
        ("block.minecraft.glowstone",        "Glowstone",          "Pedra de Luz"),
        ("block.minecraft.end_stone",        "End Stone",          "Pedra do Fim"),
        ("block.minecraft.emerald_block",    "Block of Emerald",   "Bloco de Esmeralda"),
        ("block.minecraft.redstone_block",   "Block of Redstone",  "Bloco de Redstone"),
        ("block.minecraft.crafting_table",   "Crafting Table",     "Mesa de Trabalho"),
        ("block.minecraft.furnace",          "Furnace",            "Fornalha"),
        ("block.minecraft.chest",            "Chest",              "Baú"),
        ("block.minecraft.ender_chest",      "Ender Chest",        "Baú do Fim"),
        ("block.minecraft.beacon",           "Beacon",             "Farol"),
        ("block.minecraft.spawner",          "Spawner",            "Gerador"),
    ],
    "Itens": [
        ("item.minecraft.diamond",           "Diamond",            "Diamante"),
        ("item.minecraft.emerald",           "Emerald",            "Esmeralda"),
        ("item.minecraft.iron_ingot",        "Iron Ingot",         "Lingote de Ferro"),
        ("item.minecraft.gold_ingot",        "Gold Ingot",         "Lingote de Ouro"),
        ("item.minecraft.coal",              "Coal",               "Carvão"),
        ("item.minecraft.bone",              "Bone",               "Osso"),
        ("item.minecraft.feather",           "Feather",            "Pena"),
        ("item.minecraft.string",            "String",             "Barbante"),
        ("item.minecraft.gunpowder",         "Gunpowder",          "Pólvora"),
        ("item.minecraft.arrow",             "Arrow",              "Flecha"),
        ("item.minecraft.bow",               "Bow",                "Arco"),
        ("item.minecraft.crossbow",          "Crossbow",           "Besta"),
        ("item.minecraft.shield",            "Shield",             "Escudo"),
        ("item.minecraft.trident",           "Trident",            "Tridente"),
        ("item.minecraft.fishing_rod",       "Fishing Rod",        "Cana de Pescar"),
        ("item.minecraft.compass",           "Compass",            "Bússola"),
        ("item.minecraft.clock",             "Clock",              "Relógio"),
        ("item.minecraft.shears",            "Shears",             "Tesoura"),
        ("item.minecraft.flint_and_steel",   "Flint and Steel",    "Isqueiro"),
        ("item.minecraft.ender_pearl",       "Ender Pearl",        "Pérola Ender"),
        ("item.minecraft.ender_eye",         "Eye of Ender",       "Olho do Fim"),
        ("item.minecraft.nether_star",       "Nether Star",        "Estrela do Nether"),
        ("item.minecraft.totem_of_undying",  "Totem of Undying",   "Totem da Imortalidade"),
        ("item.minecraft.book",              "Book",               "Livro"),
        ("item.minecraft.paper",             "Paper",              "Papel"),
        ("item.minecraft.stick",             "Stick",              "Graveto"),
        ("item.minecraft.netherite_ingot",   "Netherite Ingot",    "Lingote de Netherite"),
        ("item.minecraft.leather",           "Leather",            "Couro"),
        ("item.minecraft.blaze_rod",         "Blaze Rod",          "Haste de Blaze"),
        ("item.minecraft.slimeball",         "Slimeball",          "Bola de Muco"),
    ],
    "Comidas": [
        ("item.minecraft.apple",             "Apple",              "Maçã"),
        ("item.minecraft.golden_apple",      "Golden Apple",       "Maçã Dourada"),
        ("item.minecraft.bread",             "Bread",              "Pão"),
        ("item.minecraft.carrot",            "Carrot",             "Cenoura"),
        ("item.minecraft.potato",            "Potato",             "Batata"),
        ("item.minecraft.baked_potato",      "Baked Potato",       "Batata Assada"),
        ("item.minecraft.cookie",            "Cookie",             "Biscoito"),
        ("item.minecraft.pumpkin_pie",       "Pumpkin Pie",        "Torta de Abóbora"),
        ("item.minecraft.beef",              "Raw Beef",           "Carne Crua"),
        ("item.minecraft.cooked_beef",       "Steak",              "Bife"),
        ("item.minecraft.chicken",           "Raw Chicken",        "Frango Cru"),
        ("item.minecraft.cooked_chicken",    "Cooked Chicken",     "Frango Assado"),
        ("item.minecraft.porkchop",          "Raw Porkchop",       "Costeleta Crua"),
        ("item.minecraft.cooked_porkchop",   "Cooked Porkchop",    "Costeleta Assada"),
        ("item.minecraft.cod",               "Raw Cod",            "Bacalhau Cru"),
        ("item.minecraft.cooked_cod",        "Cooked Cod",         "Bacalhau Assado"),
        ("item.minecraft.salmon",            "Raw Salmon",         "Salmão Cru"),
        ("item.minecraft.cooked_salmon",     "Cooked Salmon",      "Salmão Assado"),
        ("item.minecraft.melon_slice",       "Melon Slice",        "Fatia de Melancia"),
        ("item.minecraft.sweet_berries",     "Sweet Berries",      "Frutas Doces"),
        ("item.minecraft.honey_bottle",      "Honey Bottle",       "Garrafa de Mel"),
        ("item.minecraft.mushroom_stew",     "Mushroom Stew",      "Ensopado de Cogumelo"),
        ("item.minecraft.rabbit_stew",       "Rabbit Stew",        "Ensopado de Coelho"),
        ("item.minecraft.beetroot_soup",     "Beetroot Soup",      "Sopa de Beterraba"),
    ],
    "Armas & Ferramentas": [
        ("item.minecraft.wooden_sword",      "Wooden Sword",       "Espada de Madeira"),
        ("item.minecraft.stone_sword",       "Stone Sword",        "Espada de Pedra"),
        ("item.minecraft.iron_sword",        "Iron Sword",         "Espada de Ferro"),
        ("item.minecraft.golden_sword",      "Golden Sword",       "Espada de Ouro"),
        ("item.minecraft.diamond_sword",     "Diamond Sword",      "Espada de Diamante"),
        ("item.minecraft.netherite_sword",   "Netherite Sword",    "Espada de Netherite"),
        ("item.minecraft.wooden_pickaxe",    "Wooden Pickaxe",     "Picareta de Madeira"),
        ("item.minecraft.iron_pickaxe",      "Iron Pickaxe",       "Picareta de Ferro"),
        ("item.minecraft.diamond_pickaxe",   "Diamond Pickaxe",    "Picareta de Diamante"),
        ("item.minecraft.netherite_pickaxe", "Netherite Pickaxe",  "Picareta de Netherite"),
        ("item.minecraft.wooden_axe",        "Wooden Axe",         "Machado de Madeira"),
        ("item.minecraft.iron_axe",          "Iron Axe",           "Machado de Ferro"),
        ("item.minecraft.diamond_axe",       "Diamond Axe",        "Machado de Diamante"),
        ("item.minecraft.netherite_axe",     "Netherite Axe",      "Machado de Netherite"),
        ("item.minecraft.wooden_shovel",     "Wooden Shovel",      "Pá de Madeira"),
        ("item.minecraft.iron_shovel",       "Iron Shovel",        "Pá de Ferro"),
        ("item.minecraft.diamond_shovel",    "Diamond Shovel",     "Pá de Diamante"),
    ],
    "Armaduras": [
        ("item.minecraft.leather_helmet",    "Leather Cap",        "Capacete de Couro"),
        ("item.minecraft.iron_helmet",       "Iron Helmet",        "Capacete de Ferro"),
        ("item.minecraft.golden_helmet",     "Golden Helmet",      "Capacete de Ouro"),
        ("item.minecraft.diamond_helmet",    "Diamond Helmet",     "Capacete de Diamante"),
        ("item.minecraft.netherite_helmet",  "Netherite Helmet",   "Capacete de Netherite"),
        ("item.minecraft.leather_chestplate","Leather Tunic",      "Peitoral de Couro"),
        ("item.minecraft.iron_chestplate",   "Iron Chestplate",    "Peitoral de Ferro"),
        ("item.minecraft.diamond_chestplate","Diamond Chestplate", "Peitoral de Diamante"),
        ("item.minecraft.netherite_chestplate","Netherite Chestplate","Peitoral de Netherite"),
        ("item.minecraft.leather_leggings",  "Leather Pants",      "Calças de Couro"),
        ("item.minecraft.iron_leggings",     "Iron Leggings",      "Calças de Ferro"),
        ("item.minecraft.diamond_leggings",  "Diamond Leggings",   "Calças de Diamante"),
        ("item.minecraft.netherite_leggings","Netherite Leggings", "Calças de Netherite"),
        ("item.minecraft.leather_boots",     "Leather Boots",      "Botas de Couro"),
        ("item.minecraft.iron_boots",        "Iron Boots",         "Botas de Ferro"),
        ("item.minecraft.diamond_boots",     "Diamond Boots",      "Botas de Diamante"),
        ("item.minecraft.netherite_boots",   "Netherite Boots",    "Botas de Netherite"),
        ("item.minecraft.elytra",            "Elytra",             "Élitros"),
        ("item.minecraft.turtle_helmet",     "Turtle Shell",       "Carapaça de Tartaruga"),
    ],
    "Mobs & Entidades": [
        ("entity.minecraft.zombie",          "Zombie",             "Zumbi"),
        ("entity.minecraft.skeleton",        "Skeleton",           "Esqueleto"),
        ("entity.minecraft.creeper",         "Creeper",            "Creeper"),
        ("entity.minecraft.spider",          "Spider",             "Aranha"),
        ("entity.minecraft.enderman",        "Enderman",           "Enderman"),
        ("entity.minecraft.blaze",           "Blaze",              "Blaze"),
        ("entity.minecraft.ghast",           "Ghast",              "Fantasma"),
        ("entity.minecraft.witch",           "Witch",              "Bruxa"),
        ("entity.minecraft.wither",          "Wither",             "Wither"),
        ("entity.minecraft.ender_dragon",    "Ender Dragon",       "Dragão do Fim"),
        ("entity.minecraft.guardian",        "Guardian",           "Guardião"),
        ("entity.minecraft.elder_guardian",  "Elder Guardian",     "Guardião Ancião"),
        ("entity.minecraft.shulker",         "Shulker",            "Shulker"),
        ("entity.minecraft.pig",             "Pig",                "Porco"),
        ("entity.minecraft.cow",             "Cow",                "Vaca"),
        ("entity.minecraft.sheep",           "Sheep",              "Ovelha"),
        ("entity.minecraft.chicken",         "Chicken",            "Galinha"),
        ("entity.minecraft.horse",           "Horse",              "Cavalo"),
        ("entity.minecraft.wolf",            "Wolf",               "Lobo"),
        ("entity.minecraft.cat",             "Cat",                "Gato"),
        ("entity.minecraft.villager",        "Villager",           "Aldeão"),
        ("entity.minecraft.iron_golem",      "Iron Golem",         "Golem de Ferro"),
        ("entity.minecraft.snow_golem",      "Snow Golem",         "Golem de Neve"),
        ("entity.minecraft.bee",             "Bee",                "Abelha"),
        ("entity.minecraft.axolotl",         "Axolotl",            "Axolote"),
        ("entity.minecraft.allay",           "Allay",              "Allay"),
    ],
    "Encantamentos": [
        ("enchantment.minecraft.sharpness",      "Sharpness",          "Afiação"),
        ("enchantment.minecraft.smite",          "Smite",              "Vingança Divina"),
        ("enchantment.minecraft.bane_of_arthropods","Bane of Arthropods","Perdição dos Artrópodes"),
        ("enchantment.minecraft.knockback",      "Knockback",          "Repulsão"),
        ("enchantment.minecraft.fire_aspect",    "Fire Aspect",        "Aspecto de Fogo"),
        ("enchantment.minecraft.looting",        "Looting",            "Saque"),
        ("enchantment.minecraft.efficiency",     "Efficiency",         "Eficiência"),
        ("enchantment.minecraft.silk_touch",     "Silk Touch",         "Toque de Seda"),
        ("enchantment.minecraft.fortune",        "Fortune",            "Fortuna"),
        ("enchantment.minecraft.power",          "Power",              "Poder"),
        ("enchantment.minecraft.punch",          "Punch",              "Soco"),
        ("enchantment.minecraft.flame",          "Flame",              "Chama"),
        ("enchantment.minecraft.infinity",       "Infinity",           "Infinidade"),
        ("enchantment.minecraft.protection",     "Protection",         "Proteção"),
        ("enchantment.minecraft.fire_protection","Fire Protection",    "Proteção contra Fogo"),
        ("enchantment.minecraft.feather_falling","Feather Falling",    "Queda Suave"),
        ("enchantment.minecraft.blast_protection","Blast Protection",  "Proteção contra Explosão"),
        ("enchantment.minecraft.projectile_protection","Projectile Protection","Proteção contra Projéteis"),
        ("enchantment.minecraft.respiration",    "Respiração",         "Respiração"),
        ("enchantment.minecraft.aqua_affinity",  "Aqua Affinity",      "Afinidade Aquática"),
        ("enchantment.minecraft.depth_strider",  "Depth Strider",      "Caminhante das Profundezas"),
        ("enchantment.minecraft.thorns",         "Thorns",             "Espinhos"),
        ("enchantment.minecraft.unbreaking",     "Unbreaking",         "Indestrutível"),
        ("enchantment.minecraft.mending",        "Mending",            "Correção"),
        ("enchantment.minecraft.curse_of_vanishing","Curse of Vanishing","Maldição do Desaparecimento"),
        ("enchantment.minecraft.curse_of_binding","Curse of Binding",  "Maldição da Ligação"),
        ("enchantment.minecraft.swift_sneak",    "Swift Sneak",        "Furtividade Veloz"),
        ("enchantment.minecraft.soul_speed",     "Soul Speed",         "Velocidade da Alma"),
    ],
    "Biomas": [
        ("biome.minecraft.plains",           "Plains",             "Planícies"),
        ("biome.minecraft.forest",           "Forest",             "Floresta"),
        ("biome.minecraft.taiga",            "Taiga",              "Taiga"),
        ("biome.minecraft.desert",           "Desert",             "Deserto"),
        ("biome.minecraft.jungle",           "Jungle",             "Selva"),
        ("biome.minecraft.ocean",            "Ocean",              "Oceano"),
        ("biome.minecraft.deep_ocean",       "Deep Ocean",         "Oceano Profundo"),
        ("biome.minecraft.swamp",            "Swamp",              "Pântano"),
        ("biome.minecraft.mountains",        "Mountains",          "Montanhas"),
        ("biome.minecraft.snowy_plains",     "Snowy Plains",       "Planícies Nevadas"),
        ("biome.minecraft.ice_spikes",       "Ice Spikes",         "Picos de Gelo"),
        ("biome.minecraft.mushroom_fields",  "Mushroom Fields",    "Campos de Cogumelos"),
        ("biome.minecraft.nether_wastes",    "Nether Wastes",      "Desolação do Nether"),
        ("biome.minecraft.the_end",          "The End",            "O Fim"),
        ("biome.minecraft.the_nether",       "The Nether",         "O Nether"),
        ("biome.minecraft.meadow",           "Meadow",             "Prado"),
        ("biome.minecraft.grove",            "Grove",              "Bosque"),
        ("biome.minecraft.cherry_grove",     "Cherry Grove",       "Bosque de Cerejeiras"),
        ("biome.minecraft.deep_dark",        "Deep Dark",          "Escuridão Profunda"),
        ("biome.minecraft.mangrove_swamp",   "Mangrove Swamp",     "Pântano de Manguezal"),
    ],
}


class LangEditor(QWidget):
    lang_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: dict[str, str] = {}   # key → custom translation
        self._base_lang = "pt_BR"
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(0)

        # Top bar
        top = QFrame()
        top.setStyleSheet("background:#1e1e1e;border-bottom:1px solid #2a2a2a;")
        top.setFixedHeight(44)
        tl = QHBoxLayout(top)
        tl.setContentsMargins(12,0,12,0)
        tl.setSpacing(8)

        tl.addWidget(QLabel("Categoria:"))
        self._cat = QComboBox()
        for k in LANG_ENTRIES:
            self._cat.addItem(k)
        self._cat.setFixedWidth(160)
        self._cat.currentIndexChanged.connect(self._load_table)
        tl.addWidget(self._cat)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar...")
        self._search.setFixedWidth(160)
        self._search.textChanged.connect(self._filter)
        tl.addWidget(self._search)

        tl.addWidget(QLabel("Idioma base:"))
        self._lang_combo = QComboBox()
        self._lang_combo.addItem("Português (pt_BR)", "pt_BR")
        self._lang_combo.addItem("English (en_US)",   "en_US")
        self._lang_combo.setFixedWidth(160)
        self._lang_combo.currentIndexChanged.connect(self._on_lang_change)
        tl.addWidget(self._lang_combo)

        tl.addStretch()

        reset_btn = QPushButton("Resetar selecionado")
        reset_btn.setFixedHeight(28)
        reset_btn.clicked.connect(self._reset_selected)
        tl.addWidget(reset_btn)

        self._mod_lbl = QLabel("0 modificados")
        self._mod_lbl.setStyleSheet("color:#6ab84a;font-size:11px;")
        tl.addWidget(self._mod_lbl)

        root.addWidget(top)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["Chave (ID)", "Padrão", "Seu Texto"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.setStyleSheet("""
            QTableWidget {
                background:#1a1a1a; border:none; color:#c0c0c0;
                gridline-color:#2a2a2a; font-size:12px;
            }
            QHeaderView::section {
                background:#222; color:#666; border:none;
                border-bottom:1px solid #333; padding:6px;
                font-size:10px; font-weight:bold; letter-spacing:0.5px;
            }
            QTableWidget::item { padding:4px 8px; border-bottom:1px solid #252525; }
            QTableWidget::item:selected { background:#1a3010; color:#7ec850; }
        """)
        self._table.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked |
            QTableWidget.EditTrigger.SelectedClicked)
        self._table.itemChanged.connect(self._on_item_changed)
        root.addWidget(self._table)

        # Info bar
        info = QFrame()
        info.setStyleSheet("background:#181818;border-top:1px solid #2a2a2a;")
        info.setFixedHeight(34)
        il = QHBoxLayout(info)
        il.setContentsMargins(12,0,12,0)
        tip = QLabel(
            "💡  Clique duplo na coluna 'Seu Texto' para editar  ·  "
            "Deixe em branco para usar o nome padrão do jogo")
        tip.setStyleSheet("color:#444;font-size:10px;")
        il.addWidget(tip)
        root.addWidget(info)

        self._load_table()

    def _load_table(self):
        cat = self._cat.currentText()
        entries = LANG_ENTRIES.get(cat, [])
        lang_col = 2 if self._base_lang == "pt_BR" else 1

        self._table.blockSignals(True)
        self._table.setRowCount(len(entries))

        for row, (key, en_name, pt_name) in enumerate(entries):
            default = pt_name if self._base_lang == "pt_BR" else en_name

            # Key (read-only)
            k_item = QTableWidgetItem(key)
            k_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            k_item.setForeground(QColor("#505050"))
            self._table.setItem(row, 0, k_item)

            # Default (read-only)
            d_item = QTableWidgetItem(default)
            d_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            d_item.setForeground(QColor("#666"))
            self._table.setItem(row, 1, d_item)

            # Custom
            custom = self._data.get(key, "")
            c_item = QTableWidgetItem(custom)
            c_item.setData(Qt.ItemDataRole.UserRole, key)
            if custom:
                c_item.setForeground(QColor("#6ab84a"))
            self._table.setItem(row, 2, c_item)

        self._table.blockSignals(False)

    def _on_item_changed(self, item: QTableWidgetItem):
        if item.column() != 2:
            return
        key = item.data(Qt.ItemDataRole.UserRole)
        if not key:
            return
        text = item.text().strip()
        if text:
            self._data[key] = text
            item.setForeground(QColor("#6ab84a"))
        else:
            self._data.pop(key, None)
            item.setForeground(QColor("#888"))
        self._update_count()
        self.lang_changed.emit()

    def _on_lang_change(self):
        self._base_lang = self._lang_combo.currentData()
        self._load_table()

    def _filter(self, text: str):
        text = text.lower()
        for row in range(self._table.rowCount()):
            key_item = self._table.item(row, 0)
            def_item = self._table.item(row, 1)
            visible = (not text or
                       text in (key_item.text() if key_item else "").lower() or
                       text in (def_item.text() if def_item else "").lower())
            self._table.setRowHidden(row, not visible)

    def _reset_selected(self):
        for item in self._table.selectedItems():
            if item.column() == 2:
                key = item.data(Qt.ItemDataRole.UserRole)
                self._data.pop(key, None)
                item.setText("")
                item.setForeground(QColor("#888"))
        self._update_count()
        self.lang_changed.emit()

    def _update_count(self):
        n = len(self._data)
        self._mod_lbl.setText(f"{n} modificado{'s' if n != 1 else ''}")

    def get_lang_json(self) -> dict:
        return dict(self._data)

    def load_from_dict(self, data: dict):
        self._data = dict(data)
        self._load_table()
        self._update_count()

    def load_from_file(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.load_from_dict(json.load(f))
        except Exception:
            pass
