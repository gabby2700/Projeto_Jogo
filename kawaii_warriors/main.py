"""
KAWAII WARRIORS — protótipo 3D Anime (Panda3D)
Execute com: python main.py

==================================================
COMANDOS DE ATAQUE:
  [ J ] — Ataque Normal (Corpo a corpo / Gera energia)
  [ K ] — Poder Especial (Consome energia)
  [ L ] — Trocar Arma
  [ ESPAÇO ] — Pular
==================================================
MENU: ENTER jogar | C inventário | ESC menu
SELEÇÃO: setas + 1/2/3/4 | ENTER confirmar personagem | TAB troca slot
LUTA: A/D mover | W/S profundidade | ESPAÇO pular | J ataque | K poder | L trocar arma
INVENTÁRIO: 1-4 personagens | ← → roupas | R/T atalhos | ESC sair
"""
import math
import random
from panda3d.core import (
    ClockObject, AmbientLight, DirectionalLight, Vec4, TextNode,
    WindowProperties
)
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame, DirectLabel
from direct.task import Task

CHARACTERS = [
    {"name": "Stella",  "color": (1.00, 0.48, 0.69, 1), "hair": (0.38, 0.18, 0.36, 1), "power": "Explosão de corações", "skin": (1.0, 0.85, 0.82, 1)},
    {"name": "Hana",    "color": (0.68, 0.56, 1.00, 1), "hair": (0.25, 0.22, 0.48, 1), "power": "Raio de estrelas",    "skin": (1.0, 0.88, 0.85, 1)},
    {"name": "Yuki",    "color": (1.00, 0.82, 0.48, 1), "hair": (0.52, 0.31, 0.16, 1), "power": "Chuva de doces",      "skin": (1.0, 0.90, 0.84, 1)},
    {"name": "Momo",    "color": (0.95, 0.55, 0.75, 1), "hair": (0.85, 0.35, 0.55, 1), "power": "Bombas de algodão",  "skin": (1.0, 0.87, 0.86, 1)},
]

OUTFITS = [
    ("Clássico",  (1.00, 0.86, 0.93, 1)),
    ("Pijama",    (0.60, 0.83, 1.00, 1)),
    ("Princesa",  (1.00, 0.82, 0.42, 1)),
    ("Nuvem",     (0.72, 1.00, 0.89, 1)),
    ("Sorvete",   (0.98, 0.75, 0.85, 1)),
    ("Estrelinha",(0.85, 0.78, 1.00, 1)),
]

WEAPONS = [
    "Varinha estrela",
    "Martelo de espuma",
    "Microfone mágico",
    "Arco de confete",
    "Bastão de algodão",
]

PASTEL = {
    "floor1": (0.92, 0.95, 1.00, 1),
    "floor2": (0.78, 0.85, 0.98, 1),
    "grass":  (0.55, 0.85, 0.65, 1),
    "stone":  (0.72, 0.78, 0.90, 1),
    "cream":  (1.00, 0.92, 0.95, 1),
    "cone":   (0.95, 0.78, 0.55, 1),
    "pink":   (1.00, 0.70, 0.82, 1),
    "purple": (0.75, 0.65, 0.95, 1),
    "blue":   (0.65, 0.80, 1.00, 1),
}


class KawaiiWarriors(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        props = WindowProperties()
        props.setTitle("Kawaii Warriors — Anime 3D")
        props.setSize(1280, 720)
        self.win.requestProperties(props)

        self.setBackgroundColor(0.12, 0.08, 0.22, 1)

        self.camLens.setFov(50)
        self.camera.setPos(0, -22, 11)
        self.camera.lookAt(0, 0, 1.8)

        self.state = "menu"
        self.selected = [0, 1]
        self.sel_slot = 0
        self.cursor = 0
        self.outfit = 0
        self.weapon = 0
        self.player = None
        self.enemy = None
        self.preview = None
        self.energy = 0
        self.enemy_energy = 0
        self.player_hp = 100
        self.enemy_hp = 100
        self.player_vz = 0
        self.enemy_cooldown = 0
        self.attack_timer = 0
        self.special_timer = 0
        self.restart_timer = 0  # Temporizador para reiniciar a partida automaticamente
        self.elapsed = 0
        self.keys = {k: False for k in ["a", "d", "w", "s"]}

        self.select_ui = []
        self.portrait_frames = []
        self.portrait_labels = []

        self.world = self.render.attachNewNode("world")
        self.build_lighting()
        self.build_candy_arena()
        self.build_decorations()
        self.setup_text()
        self.build_health_bars()  # Inicializa as barras de vida visuais
        self.bind_controls()
        self.taskMgr.add(self.update, "game-update")
        self.show_menu()

    def build_lighting(self):
        ambient = AmbientLight("soft-ambient")
        ambient.setColor(Vec4(0.75, 0.72, 0.85, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        sun = DirectionalLight("sun")
        sun.setColor(Vec4(1.0, 0.95, 0.88, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-20, -70, 0)
        self.render.setLight(sun_np)

    def model(self, parent, pos=(0, 0, 0), scale=1, color=None, hpr=None):
        node = self.loader.loadModel("models/misc/sphere")
        node.reparentTo(parent)
        node.setPos(*pos)
        if isinstance(scale, (tuple, list)):
            node.setScale(*scale)
        else:
            node.setScale(scale)
        if color:
            node.setColor(*color)
        if hpr:
            node.setHpr(*hpr)
        return node

    def build_candy_arena(self):
        self.model(self.world, (0, 0, -0.6), (9.5, 9.5, 0.7), PASTEL["stone"])
        self.model(self.world, (0, 0, -1.2), (8.2, 8.2, 0.6), (0.55, 0.62, 0.78, 1))
        self.model(self.world, (0, 0, -1.7), (6.5, 6.5, 0.55), (0.45, 0.50, 0.68, 1))

        tile = 1.15
        for ix in range(-3, 4):
            for iy in range(-3, 4):
                c = PASTEL["floor1"] if (ix + iy) % 2 == 0 else PASTEL["floor2"]
                self.model(self.world, (ix * tile, iy * tile, 0.02),
                           (tile * 0.48, tile * 0.48, 0.08), c)

        for i in range(28):
            a = math.tau * i / 28
            r = 4.6
            self.model(self.world, (math.cos(a) * r, math.sin(a) * r, 0.12),
                       (0.18, 0.18, 0.12), (1.0, 0.88, 0.55, 1))

        for i in range(40):
            a = math.tau * i / 40
            r = random.uniform(5.0, 6.8)
            self.model(self.world, (math.cos(a) * r, math.sin(a) * r, 0.15),
                       (0.22, 0.22, 0.18), PASTEL["grass"])

        for px, py in [(-6.2, -6.2), (6.2, -6.2), (-6.2, 6.2), (6.2, 6.2)]:
            self.model(self.world, (px, py, 0.9), (0.85, 0.85, 1.6), PASTEL["cone"])
            self.model(self.world, (px, py, 2.4), (1.1, 1.1, 1.0), PASTEL["cream"])
            self.model(self.world, (px + 0.3, py - 0.2, 3.1), (0.7, 0.7, 0.65), PASTEL["pink"])
            self.model(self.world, (px, py, 3.7), (0.25, 0.25, 0.25), (1.0, 0.25, 0.4, 1))

        for tx, ty in [(-7.5, 0), (7.5, 0), (0, -7.5), (0, 7.5)]:
            self.model(self.world, (tx, ty, 1.4), (1.0, 1.0, 2.2), PASTEL["stone"])
            self.model(self.world, (tx, ty, 3.3), (1.3, 1.3, 1.1), PASTEL["purple"])
            self.model(self.world, (tx, ty, 4.3), (0.15, 0.5, 0.4), PASTEL["blue"])

        for i in range(16):
            a = math.tau * i / 16
            r = 7.8
            col = random.choice([PASTEL["pink"], PASTEL["purple"], PASTEL["blue"], (0.9, 0.95, 1.0, 1)])
            c = self.model(self.world, (math.cos(a) * r, math.sin(a) * r, 0.6),
                           (0.22, 0.22, 0.7), col)
            c.setH(i * 22)

    def build_decorations(self):
        for _ in range(8):
            x = random.choice([-22, 22])
            y = random.choice([-22, 22])
            z = random.uniform(10, 16)
            cloud = self.world.attachNewNode("cloud")
            for j in range(5):
                self.model(cloud, (j * 0.7 - 1.4, random.uniform(-0.3, 0.3), 0),
                           (0.85, 0.55, 0.42), (0.95, 0.92, 1.0, 0.75))
            cloud.setPos(x, y, z)

        for x, y, z, s in [(-12, 9, -1.5, 1.4), (13, 11, 0.5, 1.7),
                           (-14, -10, 1, 1.2), (15, -12, -0.8, 1.5)]:
            self.model(self.world, (x, y, z), (s, s, 0.4), PASTEL["stone"])
            self.model(self.world, (x, y, z + 0.7 * s), (0.55 * s, 0.55 * s, 0.9 * s),
                       (0.48, 0.58, 0.62, 1))

    def setup_text(self):
        self.title = OnscreenText(
            text="KAWAII WARRIORS", pos=(0, 0.88), scale=0.078,
            fg=(1.0, 0.45, 0.75, 1), shadow=(0.15, 0.05, 0.25, 0.7),
            align=TextNode.ACenter
        )
        self.info = OnscreenText(
            text="", pos=(0, 0.72), scale=0.040,
            fg=(0.95, 0.9, 1.0, 1), align=TextNode.ACenter, mayChange=True
        )
        self.hud = OnscreenText(
            text="", pos=(0, 0.95), scale=0.036,
            fg=(1, 0.95, 1, 1), align=TextNode.ACenter, mayChange=True
        )
        self.bottom = OnscreenText(
            text="", pos=(0, -0.92), scale=0.032,
            fg=(0.9, 0.85, 1.0, 1), align=TextNode.ACenter, mayChange=True
        )

    # ------------------------------------------------------------------
    # BARRAS DE VIDA (UI)
    # ------------------------------------------------------------------
    def build_health_bars(self):
        # Fundo e barra de vida do Jogador (Esquerda)
        self.player_bar_bg = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.8),
            frameSize=(-0.45, 0.45, -0.035, 0.035),
            pos=(-0.5, 0, 0.85)
        )
        self.player_bar_fill = DirectFrame(
            frameColor=(0.2, 0.85, 0.3, 1),
            frameSize=(0, 0.88, -0.025, 0.025),
            pos=(-0.94, 0, 0.85)
        )

        # Fundo e barra de vida do Inimigo (Direita)
        self.enemy_bar_bg = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.8),
            frameSize=(-0.45, 0.45, -0.035, 0.035),
            pos=(0.5, 0, 0.85)
        )
        self.enemy_bar_fill = DirectFrame(
            frameColor=(0.9, 0.2, 0.3, 1),
            frameSize=(0, 0.88, -0.025, 0.025),
            pos=(0.06, 0, 0.85)
        )

        self.hide_health_bars()

    def update_health_bars(self):
        p_pct = max(0.0, self.player_hp / 100.0)
        e_pct = max(0.0, self.enemy_hp / 100.0)

        # Ajusta a largura da barra proporcionalmente à vida
        self.player_bar_fill["frameSize"] = (0, 0.88 * p_pct, -0.025, 0.025)
        self.enemy_bar_fill["frameSize"] = (0, 0.88 * e_pct, -0.025, 0.025)

    def show_health_bars(self):
        self.player_bar_bg.show()
        self.player_bar_fill.show()
        self.enemy_bar_bg.show()
        self.enemy_bar_fill.show()

    def hide_health_bars(self):
        self.player_bar_bg.hide()
        self.player_bar_fill.hide()
        self.enemy_bar_bg.hide()
        self.enemy_bar_fill.hide()

    def bind_controls(self):
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(key + "-up", self.set_key, [key, False])

        self.accept("enter", self.enter_action)
        self.accept("escape", self.escape_action)
        self.accept("c", self.open_inventory)

        for i in range(4):
            self.accept(str(i + 1), self.choose_char, [i])

        self.accept("space", self.jump)
        self.accept("j", self.normal_attack)
        self.accept("k", self.special_attack)
        self.accept("l", self.switch_weapon)

        self.accept("arrow_left", self.move_cursor, [-1, 0])
        self.accept("arrow_right", self.move_cursor, [1, 0])
        self.accept("arrow_up", self.move_cursor, [0, -1])
        self.accept("arrow_down", self.move_cursor, [0, 1])

        self.accept("r", self.cycle_outfit)
        self.accept("t", self.cycle_weapon)
        self.accept("tab", self.next_slot)

    def set_key(self, key, value):
        self.keys[key] = value

    # ------------------------------------------------------------------
    # MENU
    # ------------------------------------------------------------------
    def show_menu(self):
        self.state = "menu"
        self.hide_health_bars()
        self.clear_select_ui()
        if self.preview:
            self.preview.removeNode()
            self.preview = None
        self.info.setText("Aventura mágica nas ilhas de doce!\nENTER — jogar     C — inventário")
        self.hud.setText("")
        self.bottom.setText("Atalhos de Luta: [J] Atacar  |  [K] Poder Especial  |  [L] Trocar Arma  |  [ESPAÇO] Pular")
        self.world.show()

    def enter_action(self):
        if self.state == "menu":
            self.open_select_screen()
        elif self.state == "select":
            self.selected[self.sel_slot] = self.cursor
            if self.sel_slot == 0:
                self.sel_slot = 1
                self.update_select_ui()
            else:
                self.start_battle()
        elif self.state == "battle" and (self.player_hp <= 0 or self.enemy_hp <= 0):
            self.start_battle()
        elif self.state == "inventory":
            self.show_menu()

    def escape_action(self):
        if self.state != "menu":
            self.show_menu()

    # ------------------------------------------------------------------
    # TELA DE SELEÇÃO ESTILO FIGHTING GAME
    # ------------------------------------------------------------------
    def open_select_screen(self):
        self.state = "select"
        self.hide_health_bars()
        self.sel_slot = 0
        self.cursor = self.selected[0]
        self.clear_select_ui()
        self.build_select_ui()
        self.update_select_ui()
        self.spawn_preview(self.cursor)

    def clear_select_ui(self):
        for item in self.select_ui:
            try:
                item.destroy()
            except Exception:
                pass
        self.select_ui = []
        self.portrait_frames = []
        self.portrait_labels = []

    def build_select_ui(self):
        title = OnscreenText(
            text="SELECIONE OS PERSONAGENS",
            pos=(0.25, 0.82), scale=0.055,
            fg=(1.0, 0.85, 0.3, 1), shadow=(0, 0, 0, 0.6),
            align=TextNode.ACenter
        )
        self.select_ui.append(title)

        bg = DirectFrame(
            frameColor=(0.08, 0.05, 0.15, 0.75),
            frameSize=(-0.55, 0.55, -0.55, 0.55),
            pos=(0.45, 0, 0.05)
        )
        self.select_ui.append(bg)

        positions = [
            (-0.28, 0.22), (0.28, 0.22),
            (-0.28, -0.22), (0.28, -0.22)
        ]
        for i, (px, py) in enumerate(positions):
            ch = CHARACTERS[i]
            frame = DirectFrame(
                frameColor=ch["color"],
                frameSize=(-0.20, 0.20, -0.18, 0.18),
                pos=(0.45 + px, 0, py),
                relief=1, borderWidth=(0.02, 0.02)
            )
            self.portrait_frames.append(frame)
            self.select_ui.append(frame)

            label = DirectLabel(
                text=ch["name"],
                scale=0.045,
                pos=(0.45 + px, 0, py - 0.02),
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 0.8),
                frameColor=(0, 0, 0, 0),
                text_align=TextNode.ACenter
            )
            self.portrait_labels.append(label)
            self.select_ui.append(label)

            num = DirectLabel(
                text=str(i + 1),
                scale=0.035,
                pos=(0.45 + px - 0.14, 0, py + 0.12),
                text_fg=(1, 1, 0.6, 1),
                frameColor=(0, 0, 0, 0)
            )
            self.select_ui.append(num)

        self.slot_info = OnscreenText(
            text="", pos=(-0.55, -0.55), scale=0.038,
            fg=(1, 0.9, 1, 1), align=TextNode.ACenter, mayChange=True
        )
        self.select_ui.append(self.slot_info)

        instr = OnscreenText(
            text="← → ↑ ↓  navegar   |   ENTER confirmar   |   TAB trocar slot   |   1-4 atalho",
            pos=(0, -0.85), scale=0.028,
            fg=(0.8, 0.75, 0.95, 1), align=TextNode.ACenter
        )
        self.select_ui.append(instr)

    def update_select_ui(self):
        for i, frame in enumerate(self.portrait_frames):
            ch = CHARACTERS[i]
            if i == self.cursor:
                frame["frameColor"] = (1.0, 0.9, 0.3, 1)
            elif i in self.selected[:self.sel_slot + 1]:
                frame["frameColor"] = (0.3, 1.0, 0.5, 1)
            else:
                frame["frameColor"] = ch["color"]

        names = [CHARACTERS[i]["name"] for i in self.selected]
        slot_txt = f"SLOT {self.sel_slot + 1}/2  →  {CHARACTERS[self.cursor]['name']}\n"
        slot_txt += f"Time: {names[0]}"
        if self.sel_slot >= 1:
            slot_txt += f"  +  {names[1]}"
        else:
            slot_txt += "  +  ???"
        slot_txt += f"\nPoder: {CHARACTERS[self.cursor]['power']}"
        self.slot_info.setText(slot_txt)

        self.info.setText("")
        self.hud.setText("")
        self.bottom.setText("")

    def move_cursor(self, dx, dy):
        if self.state != "select":
            if self.state == "inventory":
                if dx != 0:
                    self.change_item(dx)
            return

        row = self.cursor // 2
        col = self.cursor % 2
        col = max(0, min(1, col + dx))
        row = max(0, min(1, row + dy))
        self.cursor = row * 2 + col
        self.update_select_ui()
        self.spawn_preview(self.cursor)

    def choose_char(self, idx):
        if self.state == "select":
            self.cursor = idx
            self.update_select_ui()
            self.spawn_preview(idx)
        elif self.state == "inventory":
            self.selected[self.sel_slot] = idx
            self.refresh_inventory_text()

    def next_slot(self):
        if self.state in ("select", "inventory"):
            self.sel_slot = 1 - self.sel_slot
            if self.state == "select":
                self.cursor = self.selected[self.sel_slot]
                self.update_select_ui()
                self.spawn_preview(self.cursor)
            else:
                self.refresh_inventory_text()

    def spawn_preview(self, idx):
        if self.preview:
            self.preview.removeNode()
        self.preview = self.create_fighter(-6.5, idx, True)
        self.preview.setScale(1.35)
        self.preview.setH(25)

    # ------------------------------------------------------------------
    # INVENTÁRIO
    # ------------------------------------------------------------------
    def open_inventory(self):
        self.state = "inventory"
        self.hide_health_bars()
        self.clear_select_ui()
        if self.preview:
            self.preview.removeNode()
            self.preview = None
        self.refresh_inventory_text()

    def refresh_inventory_text(self):
        names = [CHARACTERS[i]["name"] for i in self.selected]
        self.info.setText(
            "INVENTÁRIO DE PERSONALIZAÇÃO\n"
            "1-4 personagens  |  ← → roupas  |  R roupa  |  T arma  |  TAB slot\n"
            "ESC volta ao menu"
        )
        self.bottom.setText(
            f"Slot {self.sel_slot + 1}: {names[self.sel_slot]}  •  "
            f"Roupa: {OUTFITS[self.outfit][0]}  •  Arma: {WEAPONS[self.weapon]}"
        )
        self.hud.setText("INVENTÁRIO")

    def change_item(self, direction):
        if self.state == "inventory":
            self.outfit = (self.outfit + direction) % len(OUTFITS)
            self.refresh_inventory_text()

    def cycle_outfit(self):
        if self.state == "inventory":
            self.outfit = (self.outfit + 1) % len(OUTFITS)
            self.refresh_inventory_text()

    def cycle_weapon(self):
        if self.state == "inventory":
            self.weapon = (self.weapon + 1) % len(WEAPONS)
            self.refresh_inventory_text()

    # ------------------------------------------------------------------
    # BATALHA
    # ------------------------------------------------------------------
    def start_battle(self):
        self.clear_select_ui()
        if self.preview:
            self.preview.removeNode()
            self.preview = None

        if self.player:
            self.player.removeNode()
        if self.enemy:
            self.enemy.removeNode()

        self.player = self.create_fighter(-3.2, self.selected[0], True)
        enemy_idx = (self.selected[0] + 2) % 4
        self.enemy = self.create_fighter(3.2, enemy_idx, False)

        self.player_hp = self.enemy_hp = 100
        self.energy = self.enemy_energy = 0
        self.player_vz = 0
        self.enemy_cooldown = 0
        self.attack_timer = 0
        self.special_timer = 0
        self.restart_timer = 0
        self.state = "battle"
        self.info.setText("")
        self.bottom.setText("[A/D] Mover  •  [W/S] Profundidade  •  [ESPAÇO] Pular  •  [J] Atacar  •  [K] Poder  •  [L] Trocar Arma")
        self.show_health_bars()
        self.update_health_bars()
        self.world.show()

    def create_fighter(self, x, idx, is_player):
        root = self.render.attachNewNode("fighter-" + CHARACTERS[idx]["name"])
        root.setPos(x, 0, 0)
        ch = CHARACTERS[idx]

        self.model(root, (-0.18, 0, 0.35), (0.16, 0.18, 0.42), (0.95, 0.78, 0.85, 1))
        self.model(root, (0.18, 0, 0.35), (0.16, 0.18, 0.42), (0.95, 0.78, 0.85, 1))
        self.model(root, (0, 0, 1.05), (0.48, 0.38, 0.55), ch["color"])
        self.model(root, (0, 0.02, 1.85), (0.52, 0.45, 0.52), ch["skin"])
        self.model(root, (0, 0.12, 2.15), (0.58, 0.48, 0.42), ch["hair"])
        self.model(root, (-0.42, 0.05, 1.95), (0.22, 0.2, 0.38), ch["hair"])
        self.model(root, (0.42, 0.05, 1.95), (0.22, 0.2, 0.38), ch["hair"])
        self.model(root, (-0.18, -0.38, 1.88), (0.11, 0.07, 0.16), (0.15, 0.1, 0.2, 1))
        self.model(root, (0.18, -0.38, 1.88), (0.11, 0.07, 0.16), (0.15, 0.1, 0.2, 1))
        self.model(root, (-0.15, -0.42, 1.92), (0.04, 0.03, 0.04), (1, 1, 1, 1))
        self.model(root, (0.21, -0.42, 1.92), (0.04, 0.03, 0.04), (1, 1, 1, 1))
        self.model(root, (-0.32, -0.35, 1.72), (0.09, 0.04, 0.05), (1.0, 0.55, 0.65, 1))
        self.model(root, (0.32, -0.35, 1.72), (0.09, 0.04, 0.05), (1.0, 0.55, 0.65, 1))
        self.model(root, (0, -0.02, 0.85), (0.55, 0.45, 0.22), OUTFITS[self.outfit][1])
        self.model(root, (-0.55, 0, 1.15), (0.15, 0.15, 0.38), ch["color"])
        self.model(root, (0.55, 0, 1.15), (0.15, 0.15, 0.38), ch["color"])

        self.add_weapon(root)
        return root

    def add_weapon(self, root):
        colors = [
            (1.0, 0.85, 0.3, 1), (1.0, 0.55, 0.75, 1),
            (0.55, 0.85, 1.0, 1), (0.9, 0.7, 1.0, 1), (1.0, 0.9, 0.7, 1)
        ]
        wc = colors[self.weapon % len(colors)]
        self.model(root, (0.7, -0.05, 1.35), (0.05, 0.05, 0.45), wc, (0, 0, 15))
        self.model(root, (0.7, -0.05, 1.85), (0.2, 0.2, 0.2), wc)

    def jump(self):
        if self.state == "battle" and self.player.getZ() < 0.15:
            self.player_vz = 9.5

    def normal_attack(self):
        if self.state != "battle" or self.attack_timer > 0 or self.player_hp <= 0 or self.enemy_hp <= 0:
            return
        self.attack_timer = 0.22
        dist = abs(self.enemy.getX() - self.player.getX()) + abs(self.enemy.getY() - self.player.getY())
        if dist < 2.4:
            self.enemy_hp = max(0, self.enemy_hp - 10)
            push = 0.55 if self.enemy.getX() > self.player.getX() else -0.55
            self.enemy.setX(self.enemy.getX() + push)
            self.energy = min(100, self.energy + 20)
            self.update_health_bars()

    def special_attack(self):
        if self.state != "battle" or self.energy < 40 or self.special_timer > 0 or self.player_hp <= 0 or self.enemy_hp <= 0:
            return
        self.energy -= 40
        self.special_timer = 0.55
        dist = abs(self.enemy.getX() - self.player.getX()) + abs(self.enemy.getY() - self.player.getY())
        if dist < 5.5:
            self.enemy_hp = max(0, self.enemy_hp - 26)
            push = 0.9 if self.enemy.getX() > self.player.getX() else -0.9
            self.enemy.setX(self.enemy.getX() + push)
            self.update_health_bars()

        for i in range(14):
            p = self.model(
                self.render,
                (self.player.getX() + random.uniform(-1.6, 1.6),
                 self.player.getY() + random.uniform(-1.0, 1.0),
                 random.uniform(0.8, 3.2)),
                0.14,
                (1.0, random.uniform(0.5, 0.95), random.uniform(0.7, 1.0), 1)
            )
            self.taskMgr.doMethodLater(
                0.4 + i * 0.02, self.remove_particle, "remove-magic",
                extraArgs=[p], appendTask=True
            )

    def remove_particle(self, particle, task):
        if not particle.isEmpty():
            particle.removeNode()
        return Task.done

    def switch_weapon(self):
        if self.state == "battle":
            self.weapon = (self.weapon + 1) % len(WEAPONS)
            self.bottom.setText(f"Arma: {WEAPONS[self.weapon]}  •  [A/D] Mover  •  [J] Atacar  •  [K] Poder")

    def update(self, task):
        dt = min(ClockObject.getGlobalClock().getDt(), 0.04)
        self.elapsed += dt

        if self.state == "select" and self.preview:
            self.preview.setH(self.preview.getH() + 25 * dt)

        if self.state == "battle" and self.player and self.enemy:
            # Só permite movimentação se a partida estiver rolando
            if self.player_hp > 0 and self.enemy_hp > 0:
                speed = 11.5
                dx = (1 if self.keys["d"] else 0) - (1 if self.keys["a"] else 0)
                dy = (1 if self.keys["w"] else 0) - (1 if self.keys["s"] else 0)

                new_x = max(-5.5, min(5.5, self.player.getX() + dx * speed * dt))
                new_y = max(-5.5, min(5.5, self.player.getY() + dy * speed * dt))
                self.player.setX(new_x)
                self.player.setY(new_y)

                self.player_vz -= 24 * dt
                self.player.setZ(max(0, self.player.getZ() + self.player_vz * dt))
                if self.player.getZ() <= 0:
                    self.player_vz = 0

                ex = self.enemy.getX() - self.player.getX()
                ey = self.enemy.getY() - self.player.getY()
                dist = math.hypot(ex, ey)
                if dist > 1.7:
                    self.enemy.setX(self.enemy.getX() - math.copysign(3.8 * dt, ex))
                    self.enemy.setY(self.enemy.getY() - math.copysign(3.2 * dt, ey))

                self.enemy_cooldown = max(0, self.enemy_cooldown - dt)
                if dist < 2.0 and self.enemy_cooldown <= 0:
                    self.player_hp = max(0, self.player_hp - 6)
                    self.enemy_cooldown = 0.7
                    self.update_health_bars()

                self.player.setP(math.sin(self.elapsed * 9) * 3)
                self.enemy.setP(math.sin(self.elapsed * 9 + 1.2) * 3)

                self.attack_timer = max(0, self.attack_timer - dt)
                self.special_timer = max(0, self.special_timer - dt)

            p_name = CHARACTERS[self.selected[0]]["name"]
            e_name = CHARACTERS[(self.selected[0] + 2) % 4]["name"]
            self.hud.setText(
                f"{p_name}  EN {self.energy:03d}                          {e_name}"
            )

            # Verificação de Fim de Partida
            if self.player_hp <= 0 or self.enemy_hp <= 0:
                winner = p_name if self.enemy_hp <= 0 else e_name
                self.info.setText(f"{winner} venceu a batalha! ✨\nReiniciando a partida em instantes...")
                self.bottom.setText("Pressione ENTER para reiniciar imediatamente")

                # Contagem regressiva para reiniciar a partida automaticamente (2.5 segundos)
                self.restart_timer += dt
                if self.restart_timer >= 2.5:
                    self.start_battle()

        elif self.state == "inventory":
            self.hud.setText("INVENTÁRIO DE PERSONALIZAÇÃO")
        else:
            if self.state not in ("battle", "select"):
                self.hud.setText("")

        return Task.cont


if __name__ == "__main__":
    game = KawaiiWarriors()
    game.run()