import pygame as pg, random as rdm, math, sys
from pygame.math import Vector2 as V2
pg.init()
PAUSE_BALL = pg.USEREVENT + 1
CHANGE_LEVEL = pg.USEREVENT + 2
pg.time.set_timer(PAUSE_BALL, 100)

levels = [['0002002000', '0121441210', '1201111021', '0111331110'],
          ['2000000002', '1123443211', '1201001021', '0112332110', '1111111111'],
          ['0000220000', '1123003211', '1301001031', '0012112100', '1211331121'],
          ['0000000000', '1122332211', '2222222222', '3333333333', '1114114111']]
level = 0

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((800,600))
        self.clock = pg.time.Clock()
        self.running = True
        self.level_offset = 40*len(levels[level])
        self.level = Level(self.level_offset)
        self.paddle = Paddle()
        self.ball = Ball(self.paddle.rect.midtop)
        self.debris = pg.sprite.Group()
        self.direction = 0
        self.new_game = True
        self.new_level = True
        self.pause = False
        self.score = 0
        self.over = False
        self.lives = 3
    def run(self):
        global level
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT: self.running = False
                if event.type == PAUSE_BALL: self.ball.radius += 2
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE and self.over: self.running = False
                    elif event.key == pg.K_SPACE:
                        if self.over:
                            if self.level.blocks: self.level.blocks.update(new_game=True)
                            pg.time.set_timer(CHANGE_LEVEL, 500)
                        elif self.new_game: self.new_game = False
                        else: self.pause = not self.pause
                if event.type == CHANGE_LEVEL:
                    pg.time.set_timer(CHANGE_LEVEL, 0)
                    level = 0
                    self.__init__()
                    self.score = 0
                    self.run()
            keys = pg.key.get_pressed()
            self.screen.fill((50,50,50))
            if not self.pause:
                if keys[pg.K_LEFT]: self.direction = -1
                elif keys[pg.K_RIGHT]: self.direction = 1
                else: self.direction = 0
            else: self.screen.blit(pg.font.Font(None, 140).render('PAUSE', True, 'black'), (250,200))
            self.paddle.update(self.direction)
            self.level.blocks.update(new_level=self.new_level)
            self.level.blocks.draw(self.screen)
            if self.new_level: self.level_offset -= 1
            for debris in self.debris.sprites(): debris.draw(self.screen)
            self.paddle.draw()
            self.ball.draw()
            self.screen.blit(pg.font.Font(None, 30).render(f'score: {self.score:,}   level: {level+1}', True, 'white'), (5, 570))
            for i in range(self.lives): pg.draw.circle(self.screen, 'white', (780-i*30, 580), 10)
            for i in range(3): pg.draw.circle(self.screen, 'white', (780 - i * 30, 580), 10, 1)
            pg.display.flip()
            self.clock.tick(60)
        pg.quit()
        sys.exit()

class Paddle:
    def __init__(self):
        self.surf = pg.display.get_surface()
        self.rect = pg.Rect(0, 0, 150, 30)
        self.rect.midbottom = self.surf.get_rect().midbottom - pg.math.Vector2(0, 50)
        self.speed = 15
        self.jet = Jet()
        self.image = pg.Surface(self.rect.size)
        self.mask = pg.mask.from_surface(self.image)
    def draw(self):
        self.jet.draw(self.rect.bottomleft)
        pg.draw.rect(self.surf, 'dark blue', self.rect, 0, 4)
        pg.draw.rect(self.surf, 'blue', self.rect, 2, 4)
    def update(self, direction):
        dy = int(math.sin(math.radians(pg.time.get_ticks()*.5)) * 2)
        self.rect.move_ip(direction * self.speed, dy)
        self.rect.clamp_ip(self.surf.get_rect())

class Jet:
    def __init__(self):
        self.particels = []
    def draw(self, pos):
        self.particels.append(Particle(pos))
        for p in self.particels:
            p.radius -= 1
            p.pos += V2(p.speed, 2)
            pg.draw.circle(game.screen, p.color, p.pos, p.radius)
            if p.radius <= 0: self.particels.remove(p)

class Particle:
    def __init__(self, pos):
        self.pos = pos + V2(rdm.randint(0, game.paddle.rect.w), 0)
        self.radius = rdm.randint(10, 15)
        self.speed = rdm.randint(-2, 2)
        self.color = rdm.choice(['yellow', 'orange', 'white'])

class Ball(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.ball = pg.Surface((30, 30))
        pg.draw.circle(self.ball, 'white', (15, 15), 15)
        self.ball.set_colorkey('black')
        self.mask = pg.mask.from_surface(self.ball)
        self.rect = self.ball.get_rect(midbottom=pos)
        self.speed = 8
        self.radius = 3
        self.direction = V2(rdm.choice([-1, 1]), -1)
        self.jet = []
    def draw(self):
        if game.new_game: self.rect.midbottom = game.paddle.rect.midtop
        elif not game.pause: self.update()
        else: self.blink()
        game.screen.blit(self.ball, self.rect)
    def update(self):
        pg.draw.circle(self.ball, 'white', (15, 15), 15)
        self.jet.append([pg.Surface((30, 30)), self.rect.center, 12])
        self.rect.move_ip(self.direction.normalize()*self.speed)
        if self.rect.top <= 0: self.direction.y *= -1
        if self.rect.left <= 0 or self.rect.right >= 800: self.direction.x *= -1
        if self.rect.bottom >= 600:
            if game.lives:
                game.lives -= 1
                game.new_game = True
            else:
                game.over = True
                game.screen.blit(pg.font.Font(None, 140).render('Game over', True, 'black'), (152, 252))
                game.screen.blit(pg.font.Font(None, 140).render('Game over', True, 'white'), (150, 250))
                game.screen.blit(pg.font.Font(None, 40).render('press SPACE to start again', True, 'gray'), (250, 370))
                game.screen.blit(pg.font.Font(None, 40).render('press ESC to exit', True, 'gray'), (250, 400))
        offset = V2(self.rect.topleft) - V2(game.paddle.rect.topleft)
        if game.paddle.mask.overlap(self.mask, offset):
            diff = self.rect.bottom - game.paddle.rect.top
            if diff > self.speed+2: self.direction.x *= -1
            else:
                self.rect.bottom = game.paddle.rect.top
                self.direction.x += game.direction
                self.direction.y *= -1
        for j in self.jet:
            j[2] -= 2
            j_pos = j[1] + V2(rdm.choices([-2, -1, 1, 2], k=2))
            if j[2] <= 0: self.jet.remove(j)
            pg.draw.circle(game.screen, rdm.choice(['orange', 'yellow']), j_pos, j[2])
        new_direction = self.new_direction()
        if new_direction:
            direction, block = new_direction
            self.direction.reflect_ip(direction)
            if block.state != 4: block.state -= 1
            block_pos = V2(block.rect.bottomleft)
            for x in range(14): Debris([block_pos.x + x * 5, block_pos.y - 5], block.image.get_at((x, 0)), game.debris)
            if not block.state:
                block.kill()
                game.score += 10
                if not game.level.static: self.change_level()
            else: block.update(block.state, direction)
    def new_direction(self):
        hit_list = pg.sprite.spritecollide(self, game.level.blocks, False)
        if hit_list:
            for hit in hit_list:
                game.score += 1
                if pg.sprite.collide_mask(self, hit):
                    collision_rect = self.rect.clip(hit.rect)
                    hits = [edge for edge in ['bottom', 'top', 'left', 'right'] if
                            getattr(collision_rect, edge) != getattr(self.rect, edge)]
                    text = ''.join(hits)
                    offset = V2(V2(getattr(collision_rect, text)) - V2(self.rect.center))
                    d = self.direction.as_polar()[1]
                    a = self.direction.angle_to(offset)
                    if 90 > d >= 0:
                        if text == 'topleft' and a < 0 or text in ['bottomleft', 'left']: return V2(1, 0), hit
                        else: return V2(0, 1), hit
                    elif 180 > d >= 90:
                        if text == 'topright' and -180 < a < 0 or text in ['topleft', 'top']: return V2(0, 1), hit
                        else: return V2(-1, 0), hit
                    elif -90 > d >= -180:
                        if text == 'bottomright' and (a < 0 or a > 180) or text in ['topright', 'right']: return V2(-1, 0), hit
                        else: return V2(0, -1), hit
                    else:
                        if text == 'bottomleft' and a < 0 or text in ['bottomright', 'bottom']: return V2(0, -1), hit
                        else: return V2(1, 0), hit
    def blink(self):
        pg.draw.circle(self.ball, 'orange', (15, 15), self.radius, 4)
        if self.radius >= 15:
            self.radius = 3
            pg.draw.circle(self.ball, 'white', (15, 15), 15)
    def change_level(self):
        global level
        level = level + 1 if level < len(levels)-1 else 0
        game.score += 100
        game.level_offset = 40 * len(levels[level])
        game.level.__init__(game.level_offset)
        game.paddle.rect.midbottom = (400, 550)
        game.new_game = True
        game.new_level = True
        self.jet.clear()
        self.direction = V2(rdm.choice([-1, 1]), -1)

class Level:
    def __init__(self,level_offset=0):
        self.map = levels[level]
        self.tile_size = (80,40)
        offset = pg.math.Vector2(5,5)
        self.blocks = pg.sprite.Group()
        self.static = pg.sprite.Group()
        for i, line in enumerate(self.map):
            for j, block in enumerate(line):
                if block == '4': Block((offset.x+j*self.tile_size[0], offset.y+i*self.tile_size[1]-level_offset), block, [self.blocks])
                elif block in '123': Block((offset.x+j*self.tile_size[0], offset.y+i*self.tile_size[1]-level_offset), block, [self.blocks, self.static])

class Block(pg.sprite.Sprite):
    def __init__(self, pos, state, group):
        super().__init__(group)
        self.state = int(state)
        self.image = pg.Surface((70,30))
        self.rect = self.image.get_rect(topleft=pos)
        self.mask = pg.mask.from_surface(self.image)
        self.update(self.state)
        self.move_back = None
        self.delay = 6
        self.step = 1
    def update(self, new_state=None, move=None, new_level=None, new_game=False):
        if new_game:
            block_pos = V2(self.rect.bottomleft)
            for x in range(14): Debris([block_pos.x + x * 5, block_pos.y - 5], self.image.get_at((x, 0)), game.debris)
            self.kill()
        else:
            if new_level:
                self.rect.y += self.step
                if game.level_offset <=0: game.new_level = False
            else:
                if new_state:
                    self.state = new_state
                    w, h = self.rect.size
                    self.image.fill({1: 'blue', 2: 'darkorange', 3: 'gray', 4: 'black'}.get(new_state))
                    if self.state == 1:
                        for _ in range(7): pg.draw.line(self.image, f'dodgerblue{rdm.randint(1,4)}',
                                                         (rdm.randint(-10,80), -10), (rdm.randint(-10,80), 40), rdm.randint(3,15))
                    elif self.state == 3:
                        for _ in range(10): pg.draw.circle(self.image, f'aquamarine{rdm.randint(1,4)}',
                                           (rdm.randint(0, w), rdm.randint(0, h)), rdm.randint(4, 10))
                    elif self.state == 4:
                        for _ in range(5): pg.draw.line(self.image, f'gray{rdm.randint(15,35)}',
                                                         (-10, rdm.randint(-10,40)), (80, rdm.randint(-10,40)), rdm.randint(1,4))
                        pg.draw.rect(self.image,(80,80,80),(0,0,70,30),1)
                    elif self.state == 2:
                        for _ in range(10):
                            side = rdm.randint(8, 20)
                            rect = pg.Surface((side, side))
                            rect.set_colorkey('black')
                            rect.fill(f'gold{rdm.randint(1,4)}')
                            pos = rect.get_rect(center=(rdm.randint(0, w), rdm.randint(0, h)))
                            new_rect = pg.transform.rotate(rect, rdm.randint(1, 89))
                            new_pos = new_rect.get_rect(center=pos.center)
                            self.image.blit(new_rect, new_pos)
                    if move:
                        if self.state == 4:
                            temp_pos = self.rect.center
                            self.rect.center += move * 20
                            if (pg.sprite.spritecollide(self, pg.sprite.Group([block for block in game.level.blocks if block != self]), False)
                                or self.rect.left < 0 or self.rect.right > 800):
                                self.rect.center = temp_pos
                        else:
                            self.rect.center += move * 5
                            self.move_back = move
                else:
                    if self.move_back:
                        self.delay -= 1
                        if not self.delay:
                            self.rect.center -= self.move_back * 5
                            self.move_back = None
                            self.delay = 6

class Debris(pg.sprite.Sprite):
    def __init__(self, pos, color, group):
        super().__init__(group)
        self.timer = rdm.randint(8,12)
        self.color = color
        self.x, self.y = pos
        self.speed = 0
        self.acceleration = rdm.randint(1,4)
    def draw(self, surf):
        pg.draw.rect(surf, self.color, (self.x, self.y, 5, 5))
        self.y += self.speed
        self.speed += self.acceleration * .5
        self.timer -= 1
        if not self.timer: self.kill()


if __name__ == '__main__':
    game = Game()
    game.run()