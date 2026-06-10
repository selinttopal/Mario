import pygame as pg


class Platform(object):
    def __init__(self, x, y, image, tileid=0, type_id=0):
        self.image = image
        self.rect = pg.Rect(x, y, 32, 32)

        if tileid != 0:
            self.typeID = tileid
            self.tileid = tileid
        else:
            self.typeID = type_id
            self.tileid = type_id

        self.type = 'Platform'
        self.bonus = 'empty'
        self.isActivated = False
        self.shaking_timer = 0

    def update(self, core):
        if self.shaking_timer > 0:
            self.shaking_timer -= 1

    def shake(self):
        if not self.isActivated:
            self.shaking_timer = 5

    # Player.py dosyasının hata verip oyunu kapattığı eksik fonksiyonu ekliyoruz
    def spawn_bonus(self, core):
        # Eğer blok zaten aktif edildiyse (içi boşaltıldıysa) tekrar ödül verme
        if self.isActivated:
            return

        # Bloğun içindeki ödül türüne göre haritaya ödülü doğurtuyoruz
        if self.bonus == 'mushroom':
            core.get_map().spawn_mushroom(self.rect.x, self.rect.y)
            self.isActivated = True
        elif self.bonus == 'flower':
            core.get_map().spawn_flower(self.rect.x, self.rect.y)
            self.isActivated = True
        elif self.bonus == 'coin':
            # Coin toplandığında doğrudan skora ekle ve ses çal
            core.get_map().spawn_debris(self.rect.x, self.rect.y, 1)
            core.get_map().get_player().add_coin()
            self.isActivated = True

        else:
    # Mario küçük de olsa büyük de olsa artık bu taşı un ufak et!
            self.destroy(core)

    def destroy(self, core):
        try:
            core.get_map().spawn_debris(self.rect.x, self.rect.y, 0)
        except:
            pass

        try:
            core.get_map().remove_object(self)
        except:
            pass

    def render(self, core):
        if self.image is None:
            return

        camera_pos = core.get_map().get_camera().apply(self)
        cam_x = camera_pos[0]
        cam_y = camera_pos[1]

        y_offset = 0
        if self.shaking_timer > 0:
            y_offset = -4

        if isinstance(self.image, (tuple, list)):
            if len(self.image) > 0 and isinstance(self.image[0], pg.Surface):
                if self.isActivated:
                    core.screen.blit(self.image[3], (cam_x, cam_y + y_offset))
                else:
                    core.screen.blit(self.image[0], (cam_x, cam_y + y_offset))
            return

        if isinstance(self.image, pg.Surface):
            core.screen.blit(self.image, (cam_x, cam_y + y_offset))