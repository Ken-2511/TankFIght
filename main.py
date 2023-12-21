# 因为看了B站的视频，我做了一个坦克游戏
# 先做出坦克的雏形，用键盘按键控制

import pygame
from math import sin, cos, radians

tanks = pygame.sprite.Group()
bullets = pygame.sprite.Group()
collide_bullets = pygame.sprite.Group()  # 为防止子弹一射出就被碰到，只有当子弹离开了坦克之后才进行碰撞检测


class Tank(pygame.sprite.Sprite):

    def __init__(self, screen: pygame.Surface, pos: list, img_src, keymaps: tuple, bullet_spd, direct=0):
        super().__init__(tanks)
        self.screen = screen
        self.pos = pos
        self.direct = direct  # 以上边为0，逆时针，角度制
        self.original_image = pygame.image.load(img_src)
        self.keymaps = keymaps  # keymaps的顺序是“前 后 左 右 攻击”
        self.key_states = [False, False, False, False, False]
        self.move_speed = 3
        self.rotate_speed = 2
        self.rect = self.original_image.get_rect()
        self.image = self.original_image.copy()
        self.bullet_spd = bullet_spd
        self.bullet_cnt = 1000000

    def update(self, down_keys: list, up_keys: list):
        # 更新key_states
        for k in down_keys:
            if k in self.keymaps:
                i = self.keymaps.index(k)
                self.key_states[i] = True
        for k in up_keys:
            if k in self.keymaps:
                i = self.keymaps.index(k)
                self.key_states[i] = False
        # 根据状态调用程序
        if self.key_states[0]:
            self.move(1)
        if self.key_states[1]:
            self.move(-1)
        if self.key_states[2]:
            self.rotate(1)
        if self.key_states[3]:
            self.rotate(-1)
        if self.key_states[4]:
            self.fire()
        # 确保坦克一次只发一颗子弹
        self.key_states[4] = False
        # 绘画自己
        self.image = pygame.transform.rotate(self.original_image, self.direct)
        pos = self.pos[0] - self.image.get_width() / 2, self.pos[1] - self.image.get_height() / 2
        self.rect = self.image.get_rect()
        self.rect[:2] = pos
        # 防止坦克出界，出界即死
        if pos[0] < 0 or pos[1] < 0 or pos[0] + self.image.get_width() > 1000 or pos[1] + self.image.get_height() > 700:
            self.kill()
        self.screen.blit(self.image, pos)

    def move(self, factor):
        self.pos[0] -= sin(radians(self.direct)) * factor * self.move_speed
        self.pos[1] -= cos(radians(self.direct)) * factor * self.move_speed

    def rotate(self, factor):
        self.direct += factor * self.rotate_speed

    def fire(self):
        if self.bullet_cnt > 0:
            Bullet(self.screen, self.pos.copy(), self.direct, self.bullet_spd, self)
            self.bullet_cnt -= 1


class Bullet(pygame.sprite.Sprite):

    def __init__(self, screen: pygame.Surface, pos: list, direct, speed, father: Tank):
        super().__init__(bullets)
        self.screen = screen
        self.image = pygame.image.load("bullet.png").convert_alpha(screen)
        self.pos = [pos[0] - self.image.get_width() / 2, pos[1] - self.image.get_height() / 2]
        self.direct = direct
        self.speed = speed
        self.father = father
        self.leave_father = False
        self.life = 10000
        self.rect = self.image.get_rect()

    def update(self):
        self.move(self.speed)
        self.screen.blit(self.image, self.pos)
        self.life -= self.speed
        if self.life <= 0:
            self.kill()

    def move(self, speed):
        self.pos[0] -= sin(radians(self.direct)) * speed
        self.pos[1] -= cos(radians(self.direct)) * speed
        # 遇到边界反弹
        if not 0 < self.pos[0] < 990:
            self.direct = -self.direct
        if not 0 < self.pos[1] < 690:
            self.direct = 180 - self.direct
        # 更新rect以便于碰撞检测
        self.rect[:2] = self.pos
        # 当自己离开时加入collide group，以防止子弹刚开始时打到自己
        if not self.leave_father:
            if not pygame.sprite.collide_mask(self, self.father):
                self.add(collide_bullets)
                self.leave_father = True


def test():
    screen = pygame.display.set_mode((1000, 700))
    tank1 = Tank(screen, [100, 600], "tank.png",
                 (pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_f), 50)
    tank2 = Tank(screen, [900, 600], "tank.png",
                 (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_KP_0), 3)
    clock = pygame.time.Clock()
    while True:
        keydown_events = []
        keyup_events = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keydown_events.append(event.key)
            if event.type == pygame.KEYUP:
                keyup_events.append(event.key)

        screen.fill((250, 250, 250))
        tanks.update(keydown_events, keyup_events)
        bullets.update()
        # 如果被子弹击中，就输了
        pygame.sprite.groupcollide(tanks, collide_bullets, True, True,
                                   lambda *a: bool(pygame.sprite.collide_mask(*a)))
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    test()
