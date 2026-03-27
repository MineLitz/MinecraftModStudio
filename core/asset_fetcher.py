import os
import urllib.request
import threading
from typing import Optional, Callable

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "resources", "mc_assets")
HEADERS   = {"User-Agent": "MinecraftModStudio/1.0"}

RAW_URL = ("https://raw.githubusercontent.com/InventivetalentDev/"
           "minecraft-assets/{version}/assets/minecraft/textures/{mc_path}.png")

# ── Categorized texture definitions ─────────────────────────────────────────
# Each entry: (display_name, mc_folder, texture_name)
# mc_folder is "block" or "item" — the real Minecraft texture path

CATEGORIES: dict[str, list[tuple[str, str, str]]] = {

    "Blocos": [
        ("Pedra",            "block", "stone"),
        ("Granito",          "block", "granite"),
        ("Diorito",          "block", "diorite"),
        ("Andesito",         "block", "andesite"),
        ("Grama (topo)",     "block", "grass_block_top"),
        ("Grama (lado)",     "block", "grass_block_side"),
        ("Terra",            "block", "dirt"),
        ("Paralelepípedo",   "block", "cobblestone"),
        ("Carvalho (prancha)","block","oak_planks"),
        ("Pinheiro (prancha)","block","spruce_planks"),
        ("Bétula (prancha)", "block", "birch_planks"),
        ("Selva (prancha)",  "block", "jungle_planks"),
        ("Acácia (prancha)", "block", "acacia_planks"),
        ("Carvalho Negro",   "block", "dark_oak_planks"),
        ("Areia",            "block", "sand"),
        ("Areia Vermelha",   "block", "red_sand"),
        ("Cascalho",         "block", "gravel"),
        ("Minério Ouro",     "block", "gold_ore"),
        ("Minério Ferro",    "block", "iron_ore"),
        ("Minério Carvão",   "block", "coal_ore"),
        ("Minério Diamante", "block", "diamond_ore"),
        ("Minério Esmeralda","block", "emerald_ore"),
        ("Minério Lápis",    "block", "lapis_ore"),
        ("Minério Redstone", "block", "redstone_ore"),
        ("Carvalho (tronco)","block", "oak_log"),
        ("Carvalho (topo)",  "block", "oak_log_top"),
        ("Pinheiro (tronco)","block", "spruce_log"),
        ("Bétula (tronco)",  "block", "birch_log"),
        ("Vidro",            "block", "glass"),
        ("Bloco Ouro",       "block", "gold_block"),
        ("Bloco Ferro",      "block", "iron_block"),
        ("Bloco Diamante",   "block", "diamond_block"),
        ("Bloco Esmeralda",  "block", "emerald_block"),
        ("Bloco Redstone",   "block", "redstone_block"),
        ("Bloco Lápis",      "block", "lapis_block"),
        ("Tijolos",          "block", "bricks"),
        ("Tijolos Pedra",    "block", "stone_bricks"),
        ("Obsidiana",        "block", "obsidian"),
        ("TNT (topo)",       "block", "tnt_top"),
        ("TNT (lado)",       "block", "tnt_side"),
        ("Estante",          "block", "bookshelf"),
        ("Musgo",            "block", "mossy_cobblestone"),
        ("Pedra Musgo",      "block", "mossy_stone_bricks"),
        ("Arenito (topo)",   "block", "sandstone_top"),
        ("Arenito (lado)",   "block", "sandstone"),
        ("Arenito Vermelho", "block", "red_sandstone"),
        ("Gelo",             "block", "ice"),
        ("Neve",             "block", "snow"),
        ("Abóbora (lado)",   "block", "pumpkin_side"),
        ("Abóbora (topo)",   "block", "pumpkin_top"),
        ("Jack-o-lantern",   "block", "jack_o_lantern"),
        ("Netherrack",       "block", "netherrack"),
        ("Areia Almas",      "block", "soul_sand"),
        ("Pedra do Fim",     "block", "end_stone"),
        ("Pedra Infernal",   "block", "nether_bricks"),
        ("Quartzo (lado)",   "block", "quartz_block_side"),
        ("Quartzo (topo)",   "block", "quartz_block_top"),
        ("Terracota",        "block", "terracotta"),
        ("Terracota Branca", "block", "white_terracotta"),
        ("Magma",            "block", "magma"),
        ("Lanterna do Mar",  "block", "sea_lantern"),
        ("Prismarina",       "block", "prismarine"),
        ("Basalto (lado)",   "block", "basalt"),
        ("Basalto (topo)",   "block", "basalt_top"),
        ("Ardósia",          "block", "deepslate"),
        ("Ardósia Polida",   "block", "polished_deepslate"),
        ("Lama",             "block", "mud"),
        ("Tijolo Lama",      "block", "mud_bricks"),
        ("Calcário",         "block", "calcite"),
        ("Tuff",             "block", "tuff"),
        ("Cobre (bloco)",    "block", "copper_block"),
        ("Cobre Oxidado",    "block", "oxidized_copper"),
        ("Escória",          "block", "amethyst_block"),
    ],

    "Itens": [
        ("Maçã",             "item",  "apple"),
        ("Flecha",           "item",  "arrow"),
        ("Arco",             "item",  "bow"),
        ("Besta",            "item",  "crossbow"),
        ("Escudo",           "item",  "shield"),
        ("Tridente",         "item",  "trident"),
        ("Cana de Pescar",   "item",  "fishing_rod"),
        ("Isqueiro",         "item",  "flint_and_steel"),
        ("Bússola",          "item",  "compass"),
        ("Relógio",          "item",  "clock"),
        ("Tesoura",          "item",  "shears"),
        ("Balde",            "item",  "bucket"),
        ("Balde Água",       "item",  "water_bucket"),
        ("Balde Lava",       "item",  "lava_bucket"),
        ("Balde Leite",      "item",  "milk_bucket"),
        ("Osso",             "item",  "bone"),
        ("Barbante",         "item",  "string"),
        ("Pena",             "item",  "feather"),
        ("Pólvora",          "item",  "gunpowder"),
        ("Carvão",           "item",  "coal"),
        ("Carvão Vegetal",   "item",  "charcoal"),
        ("Diamante",         "item",  "diamond"),
        ("Esmeralda",        "item",  "emerald"),
        ("Lingote Ferro",    "item",  "iron_ingot"),
        ("Lingote Ouro",     "item",  "gold_ingot"),
        ("Pepita Ouro",      "item",  "gold_nugget"),
        ("Pepita Ferro",     "item",  "iron_nugget"),
        ("Lingote Netherite","item",  "netherite_ingot"),
        ("Couro",            "item",  "leather"),
        ("Muco",             "item",  "slimeball"),
        ("Haste Blaze",      "item",  "blaze_rod"),
        ("Pó Blaze",         "item",  "blaze_powder"),
        ("Pérola Ender",     "item",  "ender_pearl"),
        ("Olho Ender",       "item",  "ender_eye"),
        ("Estrela Nether",   "item",  "nether_star"),
        ("Totem",            "item",  "totem_of_undying"),
        ("Livro",            "item",  "book"),
        ("Livro Encantado",  "item",  "enchanted_book"),
        ("Mapa",             "item",  "map"),
        ("Papel",            "item",  "paper"),
        ("Graveto",          "item",  "stick"),
        ("Sílex",            "item",  "flint"),
        ("Bola de Neve",     "item",  "snowball"),
        ("Ovo",              "item",  "egg"),
        ("Chave",            "item",  "name_tag"),
        ("Corda",            "item",  "lead"),
        ("Âmbar",            "item",  "amethyst_shard"),
        ("Cristal Echo",     "item",  "echo_shard"),
        ("Disco Music",      "item",  "music_disc_13"),
    ],

    "Comidas": [
        ("Maçã",             "item",  "apple"),
        ("Maçã Ouro",        "item",  "golden_apple"),
        ("Maçã Ouro Encant.","item",  "enchanted_golden_apple"),
        ("Pão",              "item",  "bread"),
        ("Biscoito",         "item",  "cookie"),
        ("Melancia",         "item",  "melon_slice"),
        ("Abóbora Torta",    "item",  "pumpkin_pie"),
        ("Cenoura",          "item",  "carrot"),
        ("Cenoura Ouro",     "item",  "golden_carrot"),
        ("Batata",           "item",  "potato"),
        ("Batata Assada",    "item",  "baked_potato"),
        ("Beterraba",        "item",  "beetroot"),
        ("Carne Crua",       "item",  "beef"),
        ("Bife",             "item",  "cooked_beef"),
        ("Frango Cru",       "item",  "chicken"),
        ("Frango Assado",    "item",  "cooked_chicken"),
        ("Carne Podre",      "item",  "rotten_flesh"),
        ("Porco Cru",        "item",  "porkchop"),
        ("Porco Assado",     "item",  "cooked_porkchop"),
        ("Carneiro Cru",     "item",  "mutton"),
        ("Carneiro Assado",  "item",  "cooked_mutton"),
        ("Coelho Cru",       "item",  "rabbit"),
        ("Coelho Assado",    "item",  "cooked_rabbit"),
        ("Cod Cru",          "item",  "cod"),
        ("Cod Assado",       "item",  "cooked_cod"),
        ("Salmão Cru",       "item",  "salmon"),
        ("Salmão Assado",    "item",  "cooked_salmon"),
        ("Peixe Tropical",   "item",  "tropical_fish"),
        ("Baiacu",           "item",  "pufferfish"),
        ("Cogumelo Ensopado","item",  "mushroom_stew"),
        ("Ensopado Beterraba","item", "beetroot_soup"),
        ("Torta Coelho",     "item",  "rabbit_stew"),
        ("Fruta Doce",       "item",  "sweet_berries"),
        ("Fruta Brilhante",  "item",  "glow_berries"),
        ("Alga Seca",        "item",  "dried_kelp"),
        ("Favo de Mel",      "item",  "honeycomb"),
        ("Garrafa de Mel",   "item",  "honey_bottle"),
    ],

    "Ferramentas": [
        ("Picareta Madeira",  "item", "wooden_pickaxe"),
        ("Picareta Pedra",    "item", "stone_pickaxe"),
        ("Picareta Ferro",    "item", "iron_pickaxe"),
        ("Picareta Ouro",     "item", "golden_pickaxe"),
        ("Picareta Diamante", "item", "diamond_pickaxe"),
        ("Picareta Netherite","item", "netherite_pickaxe"),
        ("Machado Madeira",   "item", "wooden_axe"),
        ("Machado Pedra",     "item", "stone_axe"),
        ("Machado Ferro",     "item", "iron_axe"),
        ("Machado Ouro",      "item", "golden_axe"),
        ("Machado Diamante",  "item", "diamond_axe"),
        ("Machado Netherite", "item", "netherite_axe"),
        ("Pá Madeira",        "item", "wooden_shovel"),
        ("Pá Pedra",          "item", "stone_shovel"),
        ("Pá Ferro",          "item", "iron_shovel"),
        ("Pá Ouro",           "item", "golden_shovel"),
        ("Pá Diamante",       "item", "diamond_shovel"),
        ("Pá Netherite",      "item", "netherite_shovel"),
        ("Enxada Madeira",    "item", "wooden_hoe"),
        ("Enxada Pedra",      "item", "stone_hoe"),
        ("Enxada Ferro",      "item", "iron_hoe"),
        ("Enxada Ouro",       "item", "golden_hoe"),
        ("Enxada Diamante",   "item", "diamond_hoe"),
        ("Enxada Netherite",  "item", "netherite_hoe"),
        ("Isqueiro",          "item", "flint_and_steel"),
        ("Tesoura",           "item", "shears"),
        ("Cana de Pescar",    "item", "fishing_rod"),
        ("Bússola",           "item", "compass"),
        ("Relógio",           "item", "clock"),
    ],

    "Armas": [
        ("Espada Madeira",    "item", "wooden_sword"),
        ("Espada Pedra",      "item", "stone_sword"),
        ("Espada Ferro",      "item", "iron_sword"),
        ("Espada Ouro",       "item", "golden_sword"),
        ("Espada Diamante",   "item", "diamond_sword"),
        ("Espada Netherite",  "item", "netherite_sword"),
        ("Arco",              "item", "bow"),
        ("Besta",             "item", "crossbow"),
        ("Tridente",          "item", "trident"),
        ("Flecha",            "item", "arrow"),
        ("Flecha Chamas",     "item", "spectral_arrow"),
    ],

    "Armaduras": [
        ("Capacete Couro",    "item", "leather_helmet"),
        ("Peitoral Couro",    "item", "leather_chestplate"),
        ("Calças Couro",      "item", "leather_leggings"),
        ("Botas Couro",       "item", "leather_boots"),
        ("Capacete Ferro",    "item", "iron_helmet"),
        ("Peitoral Ferro",    "item", "iron_chestplate"),
        ("Calças Ferro",      "item", "iron_leggings"),
        ("Botas Ferro",       "item", "iron_boots"),
        ("Capacete Ouro",     "item", "golden_helmet"),
        ("Peitoral Ouro",     "item", "golden_chestplate"),
        ("Calças Ouro",       "item", "golden_leggings"),
        ("Botas Ouro",        "item", "golden_boots"),
        ("Capacete Diamante", "item", "diamond_helmet"),
        ("Peitoral Diamante", "item", "diamond_chestplate"),
        ("Calças Diamante",   "item", "diamond_leggings"),
        ("Botas Diamante",    "item", "diamond_boots"),
        ("Capacete Netherite","item", "netherite_helmet"),
        ("Peitoral Netherite","item", "netherite_chestplate"),
        ("Calças Netherite",  "item", "netherite_leggings"),
        ("Botas Netherite",   "item", "netherite_boots"),
        ("Capacete Tartaruga","item", "turtle_helmet"),
        ("Élitros",           "item", "elytra"),
        ("Escudo",            "item", "shield"),
    ],

    "Poções": [
        ("Garrafa Vidro",     "item", "glass_bottle"),
        ("Poção",             "item", "potion"),
        ("Poção Arremesso",   "item", "splash_potion"),
        ("Poção Persistente", "item", "lingering_potion"),
        ("Exp. Garrafa",      "item", "experience_bottle"),
    ],

    "Natura": [
        ("Folha Carvalho",    "block", "oak_leaves"),
        ("Folha Pinheiro",    "block", "spruce_leaves"),
        ("Folha Bétula",      "block", "birch_leaves"),
        ("Folha Selva",       "block", "jungle_leaves"),
        ("Folha Acácia",      "block", "acacia_leaves"),
        ("Flor Dente-de-leão","block", "dandelion"),
        ("Papoula",           "block", "poppy"),
        ("Orquídea",          "block", "blue_orchid"),
        ("Tulipa Vermelha",   "block", "red_tulip"),
        ("Tulipa Laranja",    "block", "orange_tulip"),
        ("Trigo (maduro)",    "block", "wheat_stage7"),
        ("Cacto (lado)",      "block", "cactus_side"),
        ("Cacto (topo)",      "block", "cactus_top"),
        ("Cogumelo Marrom",   "block", "brown_mushroom"),
        ("Cogumelo Vermelho", "block", "red_mushroom"),
        ("Alga (planta)",     "block", "kelp_plant"),
        ("Coral Cerebro",     "block", "brain_coral"),
        ("Bambu (haste)",     "block", "bamboo_stalk"),
        ("Videira",           "block", "vine"),
        ("Lirio d'Água",      "block", "lily_pad"),
        ("Samambaia",         "block", "fern"),
        ("Grama Alta (topo)", "block", "tall_grass_top"),
        ("Grama",             "block", "short_grass"),
    ],

    "Nether & End": [
        ("Netherrack",        "block", "netherrack"),
        ("Areia Almas",       "block", "soul_sand"),
        ("Terra Almas",       "block", "soul_soil"),
        ("Cogumelo Crimson",  "block", "crimson_nylium"),
        ("Cogumelo Warped",   "block", "warped_nylium"),
        ("Fungus Crimson",    "block", "crimson_fungus"),
        ("Fungus Warped",     "block", "warped_fungus"),
        ("Minério Ouro Nether","block","nether_gold_ore"),
        ("Minério Quartzo",   "block", "nether_quartz_ore"),
        ("Tijolo Nether",     "block", "nether_bricks"),
        ("Pedra Fogo",        "block", "glowstone"),
        ("Basalto",           "block", "basalt"),
        ("Corrente",          "block", "chain"),
        ("Pedra do Fim",      "block", "end_stone"),
        ("Tijolo do Fim",     "block", "end_stone_bricks"),
        ("Haste do Fim",      "block", "end_rod"),
        ("Flor Coro",         "block", "chorus_flower"),
        ("Purpur",            "block", "purpur_block"),
    ],

    "Mobs": [
        # Hostile
        ("Zumbi",              "entity/zombie",        "zombie"),
        ("Zumbi (afogado)",    "entity/drowned",       "drowned_outer"),
        ("Esqueleto",          "entity/skeleton",      "skeleton"),
        ("Esqueleto Wither",   "entity/skeleton",      "wither_skeleton"),
        ("Creeper",            "entity/creeper",       "creeper"),
        ("Aranha",             "entity/spider",        "spider"),
        ("Aranha de Caverna",  "entity/spider",        "cave_spider"),
        ("Enderman",           "entity/enderman",      "enderman"),
        ("Blaze",              "entity/blaze",         "blaze"),
        ("Ghast",              "entity/ghast",         "ghast"),
        ("Slime",              "entity/slime",         "slime"),
        ("Cubo de Magma",      "entity/slime",         "magmacube"),
        ("Bruxa",              "entity/witch",         "witch"),
        ("Guardião",           "entity/guardian",      "guardian"),
        ("Guardião Ancião",    "entity/elder_guardian","elder_guardian"),
        ("Shulker",            "entity/shulker",       "shulker"),
        ("Phantom",            "entity/phantom",       "phantom"),
        ("Hoglin",             "entity/hoglin",        "hoglin"),
        ("Piglin",             "entity/piglin",        "piglin"),
        ("Strider",            "entity/strider",       "strider"),
        ("Pillager",           "entity/illager",       "pillager"),
        ("Ravager",            "entity/ravager",       "ravager"),
        # Neutral
        ("Lobo",               "entity/wolf",          "wolf"),
        ("Lobo Raivoso",       "entity/wolf",          "wolf_angry"),
        ("Lobo Domesticado",   "entity/wolf",          "wolf_tame"),
        ("Abelha",             "entity/bee",           "bee"),
        ("Abelha Zangada",     "entity/bee",           "bee_angry"),
        # Passive
        ("Porco",              "entity/pig",           "pig"),
        ("Vaca",               "entity/cow",           "cow"),
        ("Ovelha",             "entity/sheep",         "sheep"),
        ("Ovelha Lã",          "entity/sheep",         "sheep_fur"),
        ("Galinha",            "entity/chicken",       "chicken"),
        ("Cavalo",             "entity/horse",         "horse_white"),
        ("Burro",              "entity/horse",         "donkey"),
        ("Mula",               "entity/horse",         "mule"),
        ("Coelho",             "entity/rabbit",        "brown"),
        ("Axolote",            "entity/axolotl",       "lucy"),
        ("Gato",               "entity/cat",           "white"),
        ("Panda",              "entity/panda",         "panda"),
        ("Lula",               "entity/squid",         "squid"),
        # Special
        ("Aldeão",             "entity/villager",      "villager"),
        ("Golem de Ferro",     "entity/iron_golem",    "iron_golem"),
        ("Golem de Neve",      "entity/snow_golem",    "snow_golem"),
        ("Wither",             "entity/wither",        "wither"),
        ("Dragão do Fim",      "entity/dragon",        "dragon"),
        ("Allay",              "entity/allay",         "allay"),
    ],

    "GUI / Interface": [
        # Containers
        ("Inventário",         "gui/container",       "inventory"),
        ("Mesa de Trabalho",   "gui/container",       "crafting_table"),
        ("Fornalha",           "gui/container",       "furnace"),
        ("Baú",                "gui/container",       "generic_54"),
        ("Baú do Fim",         "gui/container",       "shulker_box"),
        ("Bigorna",            "gui/container",       "anvil"),
        ("Encantador",         "gui/container",       "enchanting_table"),
        ("Bancada do Ferreiro","gui/container",       "grindstone"),
        ("Pedra de Afiar",     "gui/container",       "stonecutter"),
        ("Tear",               "gui/container",       "loom"),
        ("Cartógrafo",         "gui/container",       "cartography_table"),
        # HUD / Icons
        ("Ícones HUD",         "gui",                 "icons"),
        ("Widgets (hotbar)",   "gui",                 "widgets"),
        ("Livro",              "gui",                 "book"),
        # Misc
        ("Tela de Título",     "gui",                 "title/mojangstudios"),
        ("Panorama 0",         "gui",                 "title/background/panorama_0"),
    ],

    "Ambiente": [
        ("Chuva",              "environment",         "rain"),
        ("Neve",               "environment",         "snow"),
        ("Sol",                "environment",         "sun"),
        ("Fases da Lua",       "environment",         "moon_phases"),
        ("Cor Folhagem Fria",  "colormap",            "foliage"),
        ("Cor Grama Padrão",   "colormap",            "grass"),
        ("Nuvens",             "environment",         "clouds"),
        ("Água Escoando",      "block",               "water_flow"),
        ("Água Parada",        "block",               "water_still"),
        ("Lava Escoando",      "block",               "lava_flow"),
        ("Lava Parada",        "block",               "lava_still"),
        ("Portal Nether",      "block",               "nether_portal"),
        ("Portal do Fim",      "block",               "end_portal"),
        ("Fogo 0",             "block",               "fire_0"),
        ("Fogo 1",             "block",               "fire_1"),
        ("Explosão",           "particle",            "explosion_emitter"),
    ],
}


def get_texture_url(version: str, mc_folder: str, tex_name: str) -> str:
    return RAW_URL.format(
        version=version,
        mc_path=f"{mc_folder}/{tex_name}"
    )


def _cache_path(version: str, mc_folder: str, tex_name: str) -> str:
    return os.path.join(CACHE_DIR, version, mc_folder, f"{tex_name}.png")


def get_texture_path(version: str, mc_folder: str, tex_name: str) -> Optional[str]:
    path = _cache_path(version, mc_folder, tex_name)
    if os.path.exists(path) and os.path.getsize(path) > 100:
        return path
    # Mark as "not found" if a sentinel file exists
    sentinel = path + ".404"
    if os.path.exists(sentinel):
        return None

    url = get_texture_url(version, mc_folder, tex_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as r:
            if r.status == 404:
                open(sentinel, "w").close()
                return None
            data = r.read()
        if len(data) < 50:
            open(sentinel, "w").close()
            return None
        with open(path, "wb") as f:
            f.write(data)
        return path
    except urllib.error.HTTPError as e:
        if e.code == 404:
            open(sentinel, "w").close()
        return None
    except Exception:
        return None


def get_texture_path_async(version: str, mc_folder: str, tex_name: str,
                            callback: Callable[[str, Optional[str]], None]):
    def worker():
        path = get_texture_path(version, mc_folder, tex_name)
        callback(tex_name, path)
    threading.Thread(target=worker, daemon=True).start()


def get_category_items(category: str) -> list[tuple[str, str, str]]:
    """Returns list of (display_name, mc_folder, tex_name) for a category."""
    return CATEGORIES.get(category, [])


def get_category_names() -> list[str]:
    return list(CATEGORIES.keys())


def prefetch_category(version: str, category: str,
                      progress_cb: Optional[Callable[[int, int, str], None]] = None):
    items = CATEGORIES.get(category, [])
    total = len(items)

    def worker():
        for i, (_, mc_folder, tex_name) in enumerate(items):
            if progress_cb:
                progress_cb(i, total, tex_name)
            get_texture_path(version, mc_folder, tex_name)
        if progress_cb:
            progress_cb(total, total, "done")

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return t
