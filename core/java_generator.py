import os
import json
import zipfile
import shutil
import urllib.request
from core.workspace import Workspace
from core.element import ModElement

GRADLE_WRAPPER_URL = (
    "https://services.gradle.org/distributions/"
    "gradle-8.8-bin.zip"
)

# Gradle wrapper jar (binary - we'll use a placeholder approach)
WRAPPER_PROPS = """\
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.8-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
"""

GRADLEW_BAT = """\
@rem Gradle startup script for Windows
@if "%DEBUG%"=="" @echo off
@rem Set local scope for the variables with windows NT shell
if "%OS%"=="Windows_NT" setlocal

set DIRNAME=%~dp0
if "%DIRNAME%"=="" set DIRNAME=.
@rem This is normally unused
set APP_BASE_NAME=%~n0
set APP_HOME=%DIRNAME%

@rem Resolve any "." and ".." in APP_HOME to make it shorter.
for %%i in ("%APP_HOME%") do set APP_HOME=%%~fi

@rem Add default JVM options here.
set DEFAULT_JVM_OPTS="-Xmx64m" "-Xms64m"

@rem Find java.exe
if defined JAVA_HOME goto findJavaFromJavaHome

set JAVA_EXE=java.exe
%JAVA_EXE% -version >NUL 2>&1
if %ERRORLEVEL% equ 0 goto execute

echo. 1>&2
echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH. 1>&2
echo. 1>&2
exit /b 1

:findJavaFromJavaHome
set JAVA_HOME=%JAVA_HOME:"=%
set JAVA_EXE=%JAVA_HOME%/bin/java.exe

if exist "%JAVA_EXE%" goto execute

echo. 1>&2
echo ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME% 1>&2
echo. 1>&2
exit /b 1

:execute
@rem Setup the command line
set CLASSPATH=%APP_HOME%\\gradle\\wrapper\\gradle-wrapper.jar

@rem Execute Gradle
"%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %GRADLE_OPTS% -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*

:end
@rem End local scope
if %ERRORLEVEL% equ 0 goto mainEnd
:fail
exit /b 1
:mainEnd
if "%OS%"=="Windows_NT" endlocal
:omega
"""


class JavaGenerator:
    def __init__(self, workspace: Workspace):
        self.ws = workspace
        self.mid = workspace.mod_id
        self.pkg = workspace.mod_id.replace("-", "_").replace(" ", "_").lower()
        self.mc = workspace.mc_version

    def generate(self, output_dir: str) -> str:
        loader = self.ws.loader.lower()
        if "fabric" in loader or "quilt" in loader:
            return self._generate_fabric(output_dir)
        elif "forge" in loader and "neo" not in loader:
            return self._generate_forge(output_dir)
        return self._generate_neoforge(output_dir)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _class_name(self):
        return "".join(w.capitalize() for w in self.mid.split("_"))

    def _write(self, path: str, content: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _write_json(self, path: str, data: dict):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _zip(self, base_dir: str, output_dir: str, name: str) -> str:
        zip_path = os.path.join(output_dir, f"{name}.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    fp = os.path.join(root, file)
                    zf.write(fp, os.path.relpath(fp, output_dir))
        return zip_path

    def _setup_gradle_wrapper(self, base: str):
        wrapper_dir = os.path.join(base, "gradle", "wrapper")
        os.makedirs(wrapper_dir, exist_ok=True)
        self._write(os.path.join(wrapper_dir, "gradle-wrapper.properties"), WRAPPER_PROPS)
        self._write(os.path.join(base, "gradlew.bat"), GRADLEW_BAT)
        # Download actual gradle-wrapper.jar
        jar_path = os.path.join(wrapper_dir, "gradle-wrapper.jar")
        if not os.path.exists(jar_path):
            try:
                jar_url = ("https://raw.githubusercontent.com/gradle/gradle/"
                           "v8.8.0/gradle/wrapper/gradle-wrapper.jar")
                urllib.request.urlretrieve(jar_url, jar_path)
            except Exception:
                # Create empty placeholder — Gradle can still bootstrap itself
                with open(jar_path, "wb") as f:
                    f.write(b"")

    def _items(self): return [e for e in self.ws.elements if e.etype == "item"]
    def _blocks(self): return [e for e in self.ws.elements if e.etype == "block"]
    def _mobs(self):   return [e for e in self.ws.elements if e.etype == "mob"]

    def _common_assets(self, assets: str, data_dir: str):
        """Generate models, lang, blockstates and loot tables."""
        items  = self._items()
        blocks = self._blocks()

        # Item models
        for el in items:
            model = {"parent": "item/handheld",
                     "textures": {"layer0": f"{self.mid}:item/{el.registry_name}"}}
            self._write_json(os.path.join(assets, "models", "item",
                                          f"{el.registry_name}.json"), model)

        # Block models + blockstates + loot tables
        for el in blocks:
            model = {"parent": "block/cube_all",
                     "textures": {"all": f"{self.mid}:block/{el.registry_name}"}}
            self._write_json(os.path.join(assets, "models", "block",
                                          f"{el.registry_name}.json"), model)
            blockstate = {"variants": {"": {"model": f"{self.mid}:block/{el.registry_name}"}}}
            self._write_json(os.path.join(assets, "blockstates",
                                          f"{el.registry_name}.json"), blockstate)
            # Block item model
            item_model = {"parent": f"{self.mid}:block/{el.registry_name}"}
            self._write_json(os.path.join(assets, "models", "item",
                                          f"{el.registry_name}.json"), item_model)
            # Loot table (drops itself)
            loot = {
                "type": "minecraft:block",
                "pools": [{
                    "rolls": 1,
                    "entries": [{"type": "minecraft:item",
                                 "name": f"{self.mid}:{el.registry_name}"}],
                    "conditions": [{"condition": "minecraft:survives_explosion"}]
                }]
            }
            self._write_json(os.path.join(data_dir, "loot_tables", "blocks",
                                          f"{el.registry_name}.json"), loot)

        # lang/en_us.json
        lang = {}
        for el in items:
            lang[f"item.{self.mid}.{el.registry_name}"] = el.name
        for el in blocks:
            lang[f"block.{self.mid}.{el.registry_name}"] = el.name
        for el in self._mobs():
            lang[f"entity.{self.mid}.{el.registry_name}"] = el.name
        if lang:
            self._write_json(os.path.join(assets, "lang", "en_us.json"), lang)

        # Placeholder textures (1x1 green PNG)
        _placeholder = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00'
            b'\x00\x10\x08\x02\x00\x00\x00\x90\x91h6\x00\x00\x00\x1bIDAT'
            b'x\x9cc\xf8\x0f\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00'
            b'\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        for el in items:
            tex = os.path.join(assets, "textures", "item", f"{el.registry_name}.png")
            os.makedirs(os.path.dirname(tex), exist_ok=True)
            if not os.path.exists(tex):
                with open(tex, "wb") as f: f.write(_placeholder)
        for el in blocks:
            tex = os.path.join(assets, "textures", "block", f"{el.registry_name}.png")
            os.makedirs(os.path.dirname(tex), exist_ok=True)
            if not os.path.exists(tex):
                with open(tex, "wb") as f: f.write(_placeholder)

    # ── NeoForge 1.21+ ────────────────────────────────────────────────────────
    def _generate_neoforge(self, output_dir: str) -> str:
        cn = self._class_name()
        base = os.path.join(output_dir, f"{self.mid}_neoforge")
        src  = os.path.join(base, "src", "main", "java", "com", self.pkg)
        res  = os.path.join(base, "src", "main", "resources")
        assets = os.path.join(res, "assets", self.mid)
        data   = os.path.join(res, "data", self.mid)

        for d in [src, os.path.join(src, "registry"),
                  os.path.join(assets, "models", "item"),
                  os.path.join(assets, "models", "block"),
                  os.path.join(assets, "textures", "item"),
                  os.path.join(assets, "textures", "block"),
                  os.path.join(assets, "blockstates"),
                  os.path.join(assets, "lang"),
                  os.path.join(data, "loot_tables", "blocks"),
                  os.path.join(res, "META-INF")]:
            os.makedirs(d, exist_ok=True)

        # Main class
        self._write(os.path.join(src, f"{cn}.java"), self._nf_main(cn))

        # ModRegistry
        self._write(os.path.join(src, "registry", "ModRegistry.java"),
                    self._nf_registry(cn))

        # mods.toml
        desc = self.ws.description.replace('"', '\\"')
        mods_toml = (
            'modLoader = "javafml"\n'
            f'loaderVersion = "[1,)"\n'
            'license = "MIT"\n\n'
            '[[mods]]\n'
            f'modId = "{self.mid}"\n'
            f'version = "{self.ws.version}"\n'
            f'displayName = "{self.ws.project_name}"\n'
            f'description = "{desc}"\n\n'
            f'[[dependencies.{self.mid}]]\n'
            '    modId = "neoforge"\n'
            '    type = "required"\n'
            f'    versionRange = "[21,)"\n'
            '    ordering = "NONE"\n'
            '    side = "BOTH"\n\n'
            f'[[dependencies.{self.mid}]]\n'
            '    modId = "minecraft"\n'
            '    type = "required"\n'
            f'    versionRange = "[{self.mc},)"\n'
            '    ordering = "NONE"\n'
            '    side = "BOTH"\n'
        )
        self._write(os.path.join(res, "META-INF", "mods.toml"), mods_toml)
        self._write(os.path.join(res, "pack.mcmeta"),
                    json.dumps({"pack": {"pack_format": 34,
                                         "description": self.ws.project_name}},
                               indent=2))

        # Gradle files
        self._write(os.path.join(base, "build.gradle"),      self._nf_build())
        self._write(os.path.join(base, "settings.gradle"),
                    f'rootProject.name = "{self.mid}"\n')
        self._write(os.path.join(base, "gradle.properties"), self._nf_props())
        self._setup_gradle_wrapper(base)

        self._common_assets(assets, data)
        self._write(os.path.join(base, "README.md"), self._readme("NeoForge"))

        return self._zip(base, output_dir, f"{self.mid}_neoforge")

    def _nf_main(self, cn: str) -> str:
        has_items  = bool(self._items())
        has_blocks = bool(self._blocks())
        return f"""\
package com.{self.pkg};

import com.{self.pkg}.registry.ModRegistry;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;

@Mod({cn}.MOD_ID)
public class {cn} {{

    public static final String MOD_ID = "{self.mid}";

    public {cn}(IEventBus modEventBus) {{
{'        ModRegistry.ITEMS.register(modEventBus);' if has_items else ''}
{'        ModRegistry.BLOCKS.register(modEventBus);' if has_blocks else ''}
        ModRegistry.CREATIVE_TAB.register(modEventBus);
    }}
}}
"""

    def _nf_registry(self, cn: str) -> str:
        items  = self._items()
        blocks = self._blocks()

        item_fields = ""
        for el in items:
            const = el.registry_name.upper()
            stack = el.props.get("max_stack", 64)
            item_fields += (
                f'    public static final DeferredItem<Item> {const} =\n'
                f'        ITEMS.registerItem("{el.registry_name}",\n'
                f'            props -> new Item(props.stacksTo({stack})));\n\n'
            )

        block_fields = ""
        for el in blocks:
            const = el.registry_name.upper()
            hard  = el.props.get("hardness", 1.5)
            res   = el.props.get("resistance", 6.0)
            block_fields += (
                f'    public static final DeferredBlock<Block> {const} =\n'
                f'        BLOCKS.registerSimpleBlock("{el.registry_name}",\n'
                f'            BlockBehaviour.Properties.of()\n'
                f'                .strength({hard}f, {res}f)\n'
                f'                .requiresCorrectToolForDrops());\n\n'
            )
            # Register block item
            block_fields += (
                f'    public static final DeferredItem<BlockItem> {const}_ITEM =\n'
                f'        ITEMS.registerSimpleBlockItem("{el.registry_name}", {const});\n\n'
            )

        all_items = [e.registry_name.upper() for e in items] + \
                    [e.registry_name.upper() + "_ITEM" for e in blocks]
        tab_entries = "\n".join(
            f'                output.accept({c});' for c in all_items
        ) if all_items else "                // no items yet"

        return f"""\
package com.{self.pkg}.registry;

import com.{self.pkg}.{cn};
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModRegistry {{

    // ── Registries ─────────────────────────────────────────────────────────
    public static final DeferredRegister.Items ITEMS =
        DeferredRegister.createItems({cn}.MOD_ID);

    public static final DeferredRegister.Blocks BLOCKS =
        DeferredRegister.createBlocks({cn}.MOD_ID);

    public static final DeferredRegister<CreativeModeTab> CREATIVE_TAB =
        DeferredRegister.create(Registries.CREATIVE_MODE_TAB, {cn}.MOD_ID);

    // ── Items ───────────────────────────────────────────────────────────────
{item_fields}
    // ── Blocks ──────────────────────────────────────────────────────────────
{block_fields}
    // ── Creative Tab ────────────────────────────────────────────────────────
    public static final var MOD_TAB = CREATIVE_TAB.register("mod_tab",
        () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.{self.mid}"))
            .icon(() -> {all_items[0] if all_items else 'Items.GRASS_BLOCK.getDefaultInstance()'}{'.getDefaultInstance()' if all_items else ''})
            .displayItems((params, output) -> {{
{tab_entries}
            }})
            .build());
}}
"""

    def _nf_build(self) -> str:
        return f"""\
plugins {{
    id 'java-library'
    id 'eclipse'
    id 'idea'
    id 'maven-publish'
    id 'net.neoforged.moddev' version '2.0.28-beta'
}}

version = project.mod_version
group = "com.{self.pkg}"

base {{
    archivesName = project.mod_id
}}

java {{
    toolchain.languageVersion = JavaLanguageVersion.of(21)
}}

neoForge {{
    version = project.neo_version
    parchment {{
        mappingsVersion = project.parchment_mappings_version
        minecraftVersion = project.parchment_minecraft_version
    }}
    mods {{
        "{self.mid}" {{
            sourceSet(sourceSets.main)
        }}
    }}
}}

repositories {{
    maven {{ url = 'https://maven.parchmentmc.org' }}
}}

dependencies {{
    // Nothing extra needed — NeoForge MDK handles everything
}}

publishing {{
    publications {{
        register('mavenJava', MavenPublication) {{
            from components.java
        }}
    }}
    repositories {{
        maven {{ url = layout.buildDirectory.dir('repo') }}
    }}
}}
"""

    def _nf_props(self) -> str:
        # NeoForge version for MC 1.21.4
        neo_versions = {
            "1.21.4": "21.4.10-beta",
            "1.21.1": "21.1.99",
            "1.21":   "21.0.167",
            "1.20.6": "20.6.119",
            "1.20.4": "20.4.237",
        }
        neo_ver = neo_versions.get(self.mc, "21.4.10-beta")
        parchment_mc = self.mc if self.mc in neo_versions else "1.21.4"
        return f"""\
org.gradle.jvmargs=-Xmx3G
org.gradle.daemon=false
org.gradle.parallel=true

minecraft_version={self.mc}
neo_version={neo_ver}
parchment_minecraft_version={parchment_mc}
parchment_mappings_version=2024.11.17

mod_id={self.mid}
mod_version={self.ws.version}
"""

    # ── Forge 1.20.x ─────────────────────────────────────────────────────────
    def _generate_forge(self, output_dir: str) -> str:
        cn = self._class_name()
        base = os.path.join(output_dir, f"{self.mid}_forge")
        src  = os.path.join(base, "src", "main", "java", "com", self.pkg)
        res  = os.path.join(base, "src", "main", "resources")
        assets = os.path.join(res, "assets", self.mid)
        data   = os.path.join(res, "data", self.mid)

        for d in [src, os.path.join(src, "registry"),
                  os.path.join(assets, "models", "item"),
                  os.path.join(assets, "models", "block"),
                  os.path.join(assets, "textures", "item"),
                  os.path.join(assets, "textures", "block"),
                  os.path.join(assets, "blockstates"),
                  os.path.join(assets, "lang"),
                  os.path.join(data, "loot_tables", "blocks"),
                  os.path.join(res, "META-INF")]:
            os.makedirs(d, exist_ok=True)

        self._write(os.path.join(src, f"{cn}.java"), self._forge_main(cn))
        self._write(os.path.join(src, "registry", "ModRegistry.java"),
                    self._forge_registry(cn))

        desc = self.ws.description.replace('"', '\\"')
        mods_toml = (
            'modLoader = "javafml"\n'
            'loaderVersion = "[47,)"\n'
            'license = "MIT"\n\n'
            '[[mods]]\n'
            f'modId = "{self.mid}"\n'
            f'version = "{self.ws.version}"\n'
            f'displayName = "{self.ws.project_name}"\n'
            f'description = "{desc}"\n\n'
            f'[[dependencies.{self.mid}]]\n'
            '    modId = "forge"\n'
            '    mandatory = true\n'
            '    versionRange = "[47,)"\n'
            '    ordering = "NONE"\n'
            '    side = "BOTH"\n'
        )
        self._write(os.path.join(res, "META-INF", "mods.toml"), mods_toml)
        self._write(os.path.join(res, "pack.mcmeta"),
                    json.dumps({"pack": {"pack_format": 22,
                                         "description": self.ws.project_name}},
                               indent=2))
        self._write(os.path.join(base, "build.gradle"),      self._forge_build())
        self._write(os.path.join(base, "settings.gradle"),
                    f'rootProject.name = "{self.mid}"\n')
        self._write(os.path.join(base, "gradle.properties"), self._forge_props())
        self._setup_gradle_wrapper(base)
        self._common_assets(assets, data)
        self._write(os.path.join(base, "README.md"), self._readme("Forge"))
        return self._zip(base, output_dir, f"{self.mid}_forge")

    def _forge_main(self, cn: str) -> str:
        return f"""\
package com.{self.pkg};

import com.{self.pkg}.registry.ModRegistry;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

@Mod({cn}.MOD_ID)
public class {cn} {{

    public static final String MOD_ID = "{self.mid}";

    public {cn}() {{
        IEventBus bus = FMLJavaModLoadingContext.get().getModEventBus();
        ModRegistry.ITEMS.register(bus);
        ModRegistry.BLOCKS.register(bus);
        ModRegistry.CREATIVE_TABS.register(bus);
    }}
}}
"""

    def _forge_registry(self, cn: str) -> str:
        items  = self._items()
        blocks = self._blocks()

        item_fields = ""
        for el in items:
            const = el.registry_name.upper()
            stack = el.props.get("max_stack", 64)
            item_fields += (
                f'    public static final RegistryObject<Item> {const} =\n'
                f'        ITEMS.register("{el.registry_name}",\n'
                f'            () -> new Item(new Item.Properties().stacksTo({stack})));\n\n'
            )

        block_fields = ""
        for el in blocks:
            const = el.registry_name.upper()
            hard  = el.props.get("hardness", 1.5)
            res   = el.props.get("resistance", 6.0)
            block_fields += (
                f'    public static final RegistryObject<Block> {const} =\n'
                f'        BLOCKS.register("{el.registry_name}",\n'
                f'            () -> new Block(BlockBehaviour.Properties.of()\n'
                f'                .strength({hard}f, {res}f)));\n\n'
                f'    public static final RegistryObject<Item> {const}_ITEM =\n'
                f'        ITEMS.register("{el.registry_name}",\n'
                f'            () -> new BlockItem({const}.get(), new Item.Properties()));\n\n'
            )

        all_const = [e.registry_name.upper() for e in items] + \
                    [e.registry_name.upper() + "_ITEM" for e in blocks]
        tab_entries = "\n".join(
            f'                output.accept({c}.get());' for c in all_const
        ) if all_const else "                // no items yet"

        return f"""\
package com.{self.pkg}.registry;

import com.{self.pkg}.{cn};
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModRegistry {{

    public static final DeferredRegister<Item> ITEMS =
        DeferredRegister.create(ForgeRegistries.ITEMS, {cn}.MOD_ID);

    public static final DeferredRegister<Block> BLOCKS =
        DeferredRegister.create(ForgeRegistries.BLOCKS, {cn}.MOD_ID);

    public static final DeferredRegister<CreativeModeTab> CREATIVE_TABS =
        DeferredRegister.create(Registries.CREATIVE_MODE_TAB, {cn}.MOD_ID);

    // ── Items ────────────────────────────────────────────────────────────────
{item_fields}
    // ── Blocks ───────────────────────────────────────────────────────────────
{block_fields}
    // ── Creative Tab ─────────────────────────────────────────────────────────
    public static final RegistryObject<CreativeModeTab> MOD_TAB =
        CREATIVE_TABS.register("mod_tab",
            () -> CreativeModeTab.builder()
                .title(Component.translatable("itemGroup.{self.mid}"))
                .icon(() -> {'ITEMS.getEntries().iterator().next().get().getDefaultInstance()' if all_const else 'new ItemStack(Items.GRASS_BLOCK)'})
                .displayItems((params, output) -> {{
{tab_entries}
                }})
                .build());
}}
"""

    def _forge_build(self) -> str:
        forge_ver = {"1.20.4": "49.0.38", "1.20.2": "48.1.0",
                     "1.20.1": "47.2.0", "1.20": "46.0.14"}.get(self.mc, "49.0.38")
        return f"""\
buildscript {{
    repositories {{
        maven {{ url = 'https://maven.minecraftforge.net' }}
        mavenCentral()
    }}
    dependencies {{
        classpath 'net.minecraftforge.gradle:ForgeGradle:6.+' {{ changing = true }}
    }}
}}

plugins {{
    id 'eclipse'
    id 'idea'
    id 'maven-publish'
    id 'net.minecraftforge.gradle' version '[6.0,6.2)'
}}

version = project.mod_version
group = 'com.{self.pkg}'
archivesBaseName = project.mod_id

java {{
    toolchain.languageVersion = JavaLanguageVersion.of(17)
    withSourcesJar()
}}

minecraft {{
    mappings channel: 'official', version: '{self.mc}'
    copyIdeResources = true
    runs {{
        client {{
            workingDirectory project.file('run')
            property 'forge.logging.console.level', 'debug'
            mods {{
                {self.mid} {{
                    source sourceSets.main
                }}
            }}
        }}
        server {{
            workingDirectory project.file('run')
            property 'forge.logging.console.level', 'debug'
            mods {{
                {self.mid} {{
                    source sourceSets.main
                }}
            }}
        }}
    }}
}}

dependencies {{
    minecraft 'net.minecraftforge:forge:{self.mc}-{forge_ver}'
}}
"""

    def _forge_props(self) -> str:
        return f"""\
org.gradle.jvmargs=-Xmx3G
org.gradle.daemon=false

minecraft_version={self.mc}
mod_id={self.mid}
mod_version={self.ws.version}
"""

    # ── Fabric ────────────────────────────────────────────────────────────────
    def _generate_fabric(self, output_dir: str) -> str:
        cn = self._class_name()
        base = os.path.join(output_dir, f"{self.mid}_fabric")
        src  = os.path.join(base, "src", "main", "java", "com", self.pkg)
        res  = os.path.join(base, "src", "main", "resources")
        assets = os.path.join(res, "assets", self.mid)
        data   = os.path.join(res, "data", self.mid)

        for d in [src, os.path.join(src, "registry"),
                  os.path.join(assets, "models", "item"),
                  os.path.join(assets, "models", "block"),
                  os.path.join(assets, "textures", "item"),
                  os.path.join(assets, "textures", "block"),
                  os.path.join(assets, "blockstates"),
                  os.path.join(assets, "lang"),
                  os.path.join(data, "loot_tables", "blocks")]:
            os.makedirs(d, exist_ok=True)

        self._write(os.path.join(src, f"{cn}.java"),      self._fabric_main(cn))
        self._write(os.path.join(src, "registry", "ModRegistry.java"),
                    self._fabric_registry(cn))

        self._write_json(os.path.join(res, "fabric.mod.json"), {
            "schemaVersion": 1,
            "id": self.mid,
            "version": self.ws.version,
            "name": self.ws.project_name,
            "description": self.ws.description,
            "authors": [self.ws.author] if self.ws.author else [],
            "environment": "*",
            "entrypoints": {"main": [f"com.{self.pkg}.{cn}"]},
            "depends": {
                "fabricloader": ">=0.15.0",
                "fabric-api":   "*",
                "minecraft":    f"~{self.mc}"
            }
        })

        self._write(os.path.join(base, "build.gradle"),     self._fabric_build())
        self._write(os.path.join(base, "settings.gradle"),
                    f'rootProject.name = "{self.mid}"\n')
        self._write(os.path.join(base, "gradle.properties"), self._fabric_props())
        self._setup_gradle_wrapper(base)
        self._common_assets(assets, data)
        self._write(os.path.join(base, "README.md"), self._readme("Fabric"))
        return self._zip(base, output_dir, f"{self.mid}_fabric")

    def _fabric_main(self, cn: str) -> str:
        return f"""\
package com.{self.pkg};

import com.{self.pkg}.registry.ModRegistry;
import net.fabricmc.api.ModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class {cn} implements ModInitializer {{

    public static final String MOD_ID = "{self.mid}";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitialize() {{
        LOGGER.info("Initializing {self.ws.project_name}");
        ModRegistry.register();
    }}
}}
"""

    def _fabric_registry(self, cn: str) -> str:
        items  = self._items()
        blocks = self._blocks()

        reg_lines = ""
        for el in items:
            const = el.registry_name.upper()
            stack = el.props.get("max_stack", 64)
            reg_lines += (
                f'    public static final Item {const} = Registry.register(\n'
                f'        Registries.ITEM,\n'
                f'        Identifier.of({cn}.MOD_ID, "{el.registry_name}"),\n'
                f'        new Item(new Item.Settings().maxCount({stack})));\n\n'
            )
        for el in blocks:
            const = el.registry_name.upper()
            hard  = el.props.get("hardness", 1.5)
            res_  = el.props.get("resistance", 6.0)
            reg_lines += (
                f'    public static final Block {const} = Registry.register(\n'
                f'        Registries.BLOCK,\n'
                f'        Identifier.of({cn}.MOD_ID, "{el.registry_name}"),\n'
                f'        new Block(AbstractBlock.Settings.create()\n'
                f'            .strength({hard}f, {res_}f)));\n\n'
                f'    public static final BlockItem {const}_ITEM = Registry.register(\n'
                f'        Registries.ITEM,\n'
                f'        Identifier.of({cn}.MOD_ID, "{el.registry_name}"),\n'
                f'        new BlockItem({const}, new Item.Settings()));\n\n'
            )

        return f"""\
package com.{self.pkg}.registry;

import com.{self.pkg}.{cn};
import net.minecraft.block.AbstractBlock;
import net.minecraft.block.Block;
import net.minecraft.item.BlockItem;
import net.minecraft.item.Item;
import net.minecraft.registry.Registries;
import net.minecraft.registry.Registry;
import net.minecraft.util.Identifier;

public class ModRegistry {{

{reg_lines}
    public static void register() {{
        // All registrations above are done statically
        // This method just triggers class loading
    }}
}}
"""

    def _fabric_build(self) -> str:
        loader_ver = {"1.21.4": "0.16.9", "1.21.1": "0.16.0",
                      "1.21": "0.15.11", "1.20.6": "0.15.6"}.get(self.mc, "0.16.9")
        api_ver    = {"1.21.4": "0.110.0+1.21.4", "1.21.1": "0.103.0+1.21.1",
                      "1.21": "0.100.8+1.21"}.get(self.mc, "0.110.0+1.21.4")
        return f"""\
plugins {{
    id 'fabric-loom' version '1.9-SNAPSHOT'
    id 'java'
}}

version = project.mod_version
group = 'com.{self.pkg}'
base {{ archivesName = project.mod_id }}

repositories {{
    maven {{ url = 'https://maven.fabricmc.net/' }}
}}

loom {{
    splitEnvironmentSourceSets()
    mods {{
        "{self.mid}" {{
            sourceSet sourceSets.main
        }}
    }}
}}

dependencies {{
    minecraft "com.mojang:minecraft:{self.mc}"
    mappings loom.officialMojangMappings()
    modImplementation "net.fabricmc:fabric-loader:{loader_ver}"
    modImplementation "net.fabricmc.fabric-api:fabric-api:{api_ver}"
}}

java {{
    toolchain.languageVersion = JavaLanguageVersion.of(21)
    withSourcesJar()
}}
"""

    def _fabric_props(self) -> str:
        return f"""\
org.gradle.jvmargs=-Xmx3G
org.gradle.parallel=true

minecraft_version={self.mc}
mod_id={self.mid}
mod_version={self.ws.version}
"""

    def _readme(self, loader: str) -> str:
        items  = self._items()
        blocks = self._blocks()
        mobs   = self._mobs()
        java_v = "21" if loader in ("NeoForge", "Fabric") else "17"
        return f"""\
# {self.ws.project_name}

Generated by **Minecraft Mod Studio**

| | |
|---|---|
| Mod ID | `{self.mid}` |
| Version | {self.ws.version} |
| Minecraft | {self.mc} |
| Loader | {loader} |
| Author | {self.ws.author or "—"} |

## Elements
- Items ({len(items)}): {", ".join(e.name for e in items) or "none"}
- Blocks ({len(blocks)}): {", ".join(e.name for e in blocks) or "none"}
- Mobs ({len(mobs)}): {", ".join(e.name for e in mobs) or "none"}

## How to build

**Requirements:** JDK {java_v}, internet connection (first run downloads Gradle + {loader})

```bash
# Windows
gradlew.bat build

# Linux / Mac
./gradlew build
```

The compiled mod will be at `build/libs/{self.mid}-{self.ws.version}.jar`

## Install in Minecraft
1. Copy the `.jar` from `build/libs/` into your `.minecraft/mods/` folder
2. Make sure {loader} {self.mc} is installed
3. Launch Minecraft

## Textures
Placeholder textures are in `src/main/resources/assets/{self.mid}/textures/`
Replace them with your 16×16 PNG textures.

> Generated by Minecraft Mod Studio — not affiliated with Mojang/Microsoft
"""
