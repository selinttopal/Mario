import pygame as pg
from pytmx.util_pygame import load_pygame

from GameUI import GameUI
from BGObject import BGObject
from Camera import Camera
from Event import Event
from Flag import Flag
from Const import *
from Platform import Platform
from Player import Player
from Goombas import Goombas
from Mushroom import Mushroom
from Flower import Flower
from Koopa import Koopa
from Tube import Tube
from PlatformDebris import PlatformDebris
from CoinDebris import CoinDebris
from Fireball import Fireball
from Text import Text


class Map(object):
    def __init__(self, world_num):
        self.obj = []
        self.obj_bg = []
        self.tubes = []
        self.debris = []
        self.mobs = []
        self.projectiles = []
        self.text_objects = []
        self.map = 0
        self.flag = None

        self.mapSize = (0, 0)
        self.sky = 0

        self.textures = {}
        self.worldNum = world_num
        self.load_world(world_num)

        self.is_mob_spawned = [False, False]
        self.score_for_killing_mob = 100
        self.score_time = 0

        self.in_event = False
        self.tick = 0
        self.time = 400

        self.oPlayer = Player(x_pos=128, y_pos=351)
        self.oCamera = Camera(self.mapSize[0] * 32, 14)
        self.oEvent = Event()
        self.oGameUI = GameUI()

    def load_world(self, world_num):
        import os
            # Aranan harita dosyasının yolunu oluşturuyoruz (Örn: worlds/1-2/W12.tmx)
        path = f"worlds/{world_num}/W{world_num.replace('-', '')}.tmx"

            # Eğer bilgisayarda o bölüme ait klasör/dosya henüz yoksa oyun ÇÖKMESİN, varsayılan 1-1'i yüklesin!
        if not os.path.exists(path):
            print(f"UYARI: {path} bulunamadı! Varsayılan olarak 1-1 haritası şablon yükleniyor.")
            tmx_data = load_pygame("worlds/1-1/W11.tmx")
        else:
            tmx_data = load_pygame(path)

        self.mapSize = (tmx_data.width, tmx_data.height)

            # --- SEVİYE NUMARASINI GÜVENLİCE ÇEKİYORUZ ---
        level_int = 1
        if world_num and '-' in str(world_num):
            try:
                level_int = int(str(world_num).split('-')[1])
            except:
                level_int = 1

            # --- ASLA ÇÖKMEYEN HİZASI DOĞRU ATMOSFER MOTORU ---
        self.sky = pg.Surface((WINDOW_W, WINDOW_H))
        chosen_color = '#5c94fc'  # Varsayılan Gündüz Mavisi

            # 1-4 KALE BÖLÜMÜ (Sabit Kırmızı) 🌋
        if str(world_num) == '1-4':
            chosen_color = '#990000'
            print(f"--- BÖLÜM {world_num}: KALE KIRMIZISI ATMOSFERİ YÜKLENDİ ---")

            # DİĞER TÜM BÖLÜMLER İÇİN RENGARENK PALET SİSTEMİ 🎨
        else:
            try:
                level_id = int(str(world_num).split('-')[1])
            except:
                level_id = 1

            color_palette = {
                1: '#5c94fc',  # Gündüz Mavisi (1-1)
                2: '#000022',  # Gece Laciverti (1-2)
                3: '#000000',  # Mağara Siyahı (1-3)
                4: '#990000',  # Kale Kırmızısı (1-4)
                5: '#700070',  # Gizemli Mor 🔮 (1-5)
                6: '#005030',  # Derin Orman Yeşili 🌲 (1-6)
                7: '#ff8c00',  # Gün Batımı Turuncusu 🌅 (1-7)
                8: '#008080',  # Egzotik Turkuaz 🌊 (1-8)
                9: '#ff69b4'  # Şeker Pembesi 🌸 (1-9)
            }
            chosen_color = color_palette.get(level_id, '#5c94fc')
            print(f"--- BÖLÜM {world_num}: RENGARENK ATMOSFER ({chosen_color}) YÜKLENDİ ---")

            # Seçilen renkle yüzeyi boyuyoruz (Artık hiçbir bloğun içinde gizli değil!)
        self.sky.fill(pg.Color(chosen_color))

            # --- BURADAN AŞAĞISI ESKİ HARİTA MATRİSİNİN DEVAMI ---
        self.map = [[0] * tmx_data.height for i in range(tmx_data.width)]


        layer_num = 0
        # --- ASLA ÇÖKMEYEN VE KATMANLARI %100 DOĞRU OKUYAN YENİ MOTOR ---
        for layer_num, layer in enumerate(tmx_data.visible_layers):
            if hasattr(layer, 'tiles'):
                for x, y, image in layer.tiles():
                    tileID = tmx_data.get_tile_gid(x, y, layer_num)

                    if image is not None:
                        if layer.name == 'Foreground':
                            if tileID == 22:
                                image = (
                                    image,
                                    tmx_data.get_tile_image(0, 15, layer_num),
                                    tmx_data.get_tile_image(1, 15, layer_num),
                                    tmx_data.get_tile_image(2, 15, layer_num)
                                )

                            self.map[x][y] = Platform(x * 32, y * 32, image, tileID)
                            self.obj.append(self.map[x][y])

                        elif layer.name == 'Background':
                            self.map[x][y] = BGObject(x * 32, y * 32, image)
                            self.obj_bg.append(self.map[x][y])

                        elif layer.name == 'Background':
                            self.map[x][y] = BGObject(x * tmx_data.tileheight, y * tmx_data.tilewidth, image)
                            self.obj_bg.append(self.map[x][y])
            layer_num += 1
            # --- 1-4 BÖLÜMÜ GARANTİLİ MANTAR VE SARSIK MOTORU 🍄 ---
            if str(world_num) == '1-4':
                # Sadece 46,8 değil; sağını solunu da kapsama alanına alıyoruz!
                for test_x in [45, 46, 47]:
                    try:
                        if self.map[test_x][8] != 0:
                            self.map[test_x][8].bonus = 'mushroom'
                            self.map[test_x][8].tileID = 22  # Kodu sarsılma moduna zorla!
                    except:
                        pass
                print("--- 1-4 BÖLÜMÜ: MANTAR BÖLGESİ AKTİF EDİLDİ ---")
        # Tubes
        self.spawn_tube(28, 10)
        self.spawn_tube(37, 9)
        self.spawn_tube(46, 8)
        self.spawn_tube(55, 8)
        self.spawn_tube(163, 10)
        self.spawn_tube(179, 10)

        # Mobs
        self.mobs.append(Goombas(736, 352, False))
        self.mobs.append(Goombas(1295, 352, True))
        self.mobs.append(Goombas(1632, 352, False))
        self.mobs.append(Goombas(1672, 352, False))
        self.mobs.append(Goombas(5570, 352, False))
        self.mobs.append(Goombas(5620, 352, False))

        # --- ÇÖKME KORUMALI YENİ MANTAR SİSTEMİ ---
        try:
            if self.map[21][8] != 0: self.map[21][8].bonus = 'mushroom'
        except:
            pass

        try:
            if self.map[78][8] != 0: self.map[78][8].bonus = 'mushroom'
        except:
            pass

        try:
            if self.map[109][4] != 0: self.map[109][4].bonus = 'mushroom'
        except:
            pass

        self.flag = Flag(6336, 48)

    def reset(self, reset_all):
        self.obj = []
        self.obj_bg = []
        self.tubes = []
        self.debris = []
        self.mobs = []
        self.is_mob_spawned = [False, False]

        self.in_event = False
        self.flag = None
        self.sky = None
        self.map = None

        self.tick = 0
        self.time = 400

        self.mapSize = (0, 0)
        self.textures = {}
        self.load_world(self.worldNum)

        self.get_event().reset()
        self.get_player().reset(reset_all)
        self.get_camera().reset()

    def get_name(self):
        return self.worldNum

    def get_player(self):
        return self.oPlayer

    def get_camera(self):
        return self.oCamera

    def get_event(self):
        return self.oEvent

    def get_ui(self):
        return self.oGameUI

    def get_blocks_for_collision(self, x, y):
        return (
            self.map[x][y - 1],
            self.map[x][y + 1],
            self.map[x][y],
            self.map[x - 1][y],
            self.map[x + 1][y],
            self.map[x + 2][y],
            self.map[x + 1][y - 1],
            self.map[x + 1][y + 1],
            self.map[x][y + 2],
            self.map[x + 1][y + 2],
            self.map[x - 1][y + 1],
            self.map[x + 2][y + 1],
            self.map[x][y + 3],
            self.map[x + 1][y + 3]
        )

    def get_blocks_below(self, x, y):
        return (
            self.map[x][y + 1],
            self.map[x + 1][y + 1]
        )

    def get_mobs(self):
        return self.mobs

    def spawn_tube(self, x_coord, y_coord):
        self.tubes.append(Tube(x_coord, y_coord))
        for y in range(y_coord, 12):
            for x in range(x_coord, x_coord + 2):
                self.map[x][y] = Platform(x * 32, y * 32, image=None, tileid=0)

    def spawn_mushroom(self, x, y):
        self.get_mobs().append(Mushroom(x, y, True))

    def spawn_goombas(self, x, y, move_direction):
        self.get_mobs().append(Goombas(x, y, move_direction))

    def spawn_koopa(self, x, y, move_direction):
        self.get_mobs().append(Koopa(x, y, move_direction))

    def spawn_flower(self, x, y):
        self.mobs.append(Flower(x, y))

    def spawn_debris(self, x, y, type):
        if type == 0:
            self.debris.append(PlatformDebris(x, y))
        elif type == 1:
            self.debris.append(CoinDebris(x, y))

    def spawn_fireball(self, x, y, move_direction):
        self.projectiles.append(Fireball(x, y, move_direction))

    def spawn_score_text(self, x, y, score=None):
        if score is None:
            self.text_objects.append(Text(str(self.score_for_killing_mob), 16, (x, y)))
            self.score_time = pg.time.get_ticks()
            if self.score_for_killing_mob < 1600:
                self.score_for_killing_mob *= 2
        else:
            self.text_objects.append(Text(str(score), 16, (x, y)))

    def remove_object(self, object):
        self.obj.remove(object)
        self.map[object.rect.x // 32][object.rect.y // 32] = 0

    def remove_whizbang(self, whizbang):
        self.projectiles.remove(whizbang)

    def remove_text(self, text_object):
        self.text_objects.remove(text_object)

    def update_player(self, core):
        self.get_player().update(core)

    def update_entities(self, core):
        for mob in self.mobs:
            mob.update(core)
            if not self.in_event:
                self.entity_collisions(core)

    def update_time(self, core):
        if not self.in_event:
            self.tick += 1
            if self.tick % 40 == 0:
                self.time -= 1
                self.tick = 0
            if self.time == 100 and self.tick == 1:
                core.get_sound().start_fast_music(core)
            elif self.time == 0:
                self.player_death(core)

    def update_score_time(self):
        if self.score_for_killing_mob != 100:
            if pg.time.get_ticks() > self.score_time + 750:
                self.score_for_killing_mob //= 2

    def entity_collisions(self, core):
        if not core.get_map().get_player().unkillable:
            for mob in self.mobs:
                mob.check_collision_with_player(core)

    def try_spawn_mobs(self, core):
        if self.get_player().rect.x > 2080 and not self.is_mob_spawned[0]:
            self.spawn_goombas(2495, 224, False)
            self.spawn_goombas(2560, 96, False)
            self.is_mob_spawned[0] = True
        elif self.get_player().rect.x > 2460 and not self.is_mob_spawned[1]:
            self.spawn_goombas(3200, 352, False)
            self.spawn_goombas(3250, 352, False)
            self.spawn_koopa(3400, 352, False)
            self.spawn_goombas(3700, 352, False)
            self.spawn_goombas(3750, 352, False)
            self.spawn_goombas(4060, 352, False)
            self.spawn_goombas(4110, 352, False)
            self.spawn_goombas(4190, 352, False)
            self.spawn_goombas(4240, 352, False)
            self.is_mob_spawned[1] = True

    def player_death(self, core):
        self.in_event = True
        self.get_player().reset_jump()
        self.get_player().reset_move()
        self.get_player().numOfLives -= 1

        if self.get_player().numOfLives == 0:
            self.get_event().start_kill(core, game_over=True)
        else:
            self.get_event().start_kill(core, game_over=False)

    def player_win(self, core):
        core.next_level()

    def update(self, core):
        self.update_entities(core)
        if not core.get_map().in_event:
            if self.get_player().inLevelUpAnimation:
                self.get_player().change_powerlvl_animation()
            elif self.get_player().inLevelDownAnimation:
                self.get_player().change_powerlvl_animation()
                self.update_player(core)
            else:
                self.update_player(core)
        else:
            self.get_event().update(core)

        for debris in self.debris:
            debris.update(core)
        for whizbang in self.projectiles:
            whizbang.update(core)
        for text_object in self.text_objects:
            text_object.update(core)

        if not self.in_event:
            self.get_camera().update(core.get_map().get_player().rect)

        self.try_spawn_mobs(core)
        self.update_time(core)
        self.update_score_time()

    def render_map(self, core):
        core.screen.blit(self.sky, (0, 0))
        for obj_group in (self.obj_bg, self.obj):
            for obj in obj_group:
                obj.render(core)
        for tube in self.tubes:
            tube.render(core)

    def render(self, core):
        core.screen.blit(self.sky, (0, 0))
        for obj in self.obj_bg:
            obj.render(core)
        for mob in self.mobs:
            mob.render(core)
        for obj in self.obj:
            obj.render(core)
        for tube in self.tubes:
            tube.render(core)
        for whizbang in self.projectiles:
            whizbang.render(core)
        for debris in self.debris:
            debris.render(core)

        self.flag.render(core)

        for text_object in self.text_objects:
            text_object.render_in_game(core)

        self.get_player().render(core)
        self.get_ui().render(core)
