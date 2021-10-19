import pygame
SX, SY = 1000, 1000
FPS = 30
def circle(screen, x, y, r, color=(255, 0, 0)):
    cof = 10
    x = x * cof + SX // 2
    y = y * cof + SY // 2
    r *= cof
    pygame.draw.circle(screen,
                                     color,
                                     (int(x), int(y)),
                                     int(r), 1)
    pygame.draw.circle(screen,
                                     (255, 255, 0),
                                     (int(x), int(y)),
                                     1)
    




from math import sqrt
from typing import Type

class Vector2:
    def __init__(self, x, y):
        self.x, self.y = x, y

    @property
    def xy(self):
        return self.x, self.y

    @xy.setter
    def xy(self, value):
        self.x, self.y = value

    @classmethod
    def Zero(cls):
        return cls(0, 0)

    def len_2(self):
        return self.x ** 2 + self.y ** 2

    def len(self):
        return sqrt(self.len_2())

    def Left(self):
        return Vector2(self.y, self.x)

    def Right(self):
        return Vector2(self.y, self.x)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
        
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    @staticmethod
    def dot(self, vec1, vec2):
        return vec1.x * vec2.x + vec1.y * vec2.y
        
    def __str__(self):
        return f"<{self.__class__.__name__}>{self.xy}"

    def copy(self):
        return self.__class__(self.x, self.y)

class Collider:
    def __init__(self, gameObject):
        self.gameObject = gameObject

    @property
    def position(self):
        return self.gameObject.position

    @position.setter
    def position(self, value):
        self.gameObject.position = value

    # check colliding for list GameObjects
    def collisions(self, objs):
        return []


class CircleCollider(Collider):
    def __init__(self, gameObject, radius=1):
        super().__init__(gameObject)
        self.radius = radius

    # check colliding for list GameObjects
    def collisions(self, objs):
        # my position
        mx, my = self.position.xy 
        # столкновения Collider
        collisions = []
        for obj in objs:
            coll = obj.collider    
            if coll is self:
                continue        
            if type(coll) is CircleCollider:
                px, py = coll.position.xy
                # проверяем соприклсновение кругов
                summ_r_2 = (self.radius + coll.radius) ** 2
                dist_2 = abs(px - mx) ** 2 + abs(py - my) ** 2 
                if dist_2 <= summ_r_2:
                    collisions.append(coll)
        return collisions



class Physbody:
    def __init__(self, gameObject, speed=Vector2.Zero()):
        self.gameObject = gameObject
        self.speed = speed
        # в текущий такт происходила ли проверка физики объекта
        self.is_update_collisions = False

    @property
    def position(self):
        return self.gameObject.position

    @position.setter
    def position(self, value):
        self.gameObject.position = value

    @property
    def collider(self):
        return self.gameObject.collider


    # обновление координаты от скорости
    def update(self): 
        self.is_update_collisions = False
        mx, my = self.position.xy 
        self.position.xy = mx + self.speed.x, my + self.speed.y
        return self.position.xy 

    # вычисление столкновений
    def collisions(self, collisions):
        
        my_pos = self.position
        sx, sy = self.speed.xy
        if type(self.collider) is CircleCollider:
            for coll in collisions:
                if type(coll) is CircleCollider:
                    coll_physbody = coll.gameObject.physbody
                    coll_pos = coll.position
                    # вектор между кругами
                    H = (coll_pos - my_pos)
                    if H.len_2() == 0:
                        continue

                    if coll_physbody:
                        sx2, sy2 = coll_physbody.speed.xy
                    else:
                        sx2, sy2 = 0, 0

                    hx, hy = H.xy
                    a = sx*hx + sy*hy - sx2*hx - sy2*hy
                    a /= H.len_2()
                    my_speed = Vector2(sx - a * hx, sy - a * hy)
                    if coll_physbody:
                        other_speed = Vector2(sx2 + a * hx, sy2 + a * hy)
                        coll_physbody.speed = other_speed
                        coll_physbody.is_update_collisions = True
                    sx, sy = my_speed.xy
        self.speed.xy = sx, sy
                    
class GameObject:
    def __init__(self, position: Vector2, Collider=None, Physbody=None, speed=Vector2.Zero(), name="GameObject"):
        self.position = position
        self.collider = Collider(self)                    
        self.physbody = Physbody(self, speed=speed)
        self.name = name

    @property
    def xy(self):
        return self.position.xy

    @xy.setter
    def xy(self, value):
        self.position.xy = value

    def __str__(self):
        return f"<{self.name}>{self.position}"

    
class Circle(GameObject):
    def __init__(self, position: Vector2, Collider=None, Physbody=None, radius=1, speed=Vector2.Zero(), name="GameObject"):
        super().__init__(position, Collider, Physbody, speed, name)
        self.collider.radius = radius
        
class Player(GameObject):
    def __init__(self, position: Vector2, speed=Vector2.Zero(), name="Player"):
        super().__init__(position, Collider=CircleCollider, Physbody=Physbody, speed=speed, name=name)
        self.collider.radius = 1
        self.max_speed = 1
        # ускорение
        self.acceleration = 0.2

    def handle_event(self, event):
        speed = self.physbody.speed.copy()
        
        if event.type == pygame.KEYDOWN:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    speed.x = min(-self.max_speed, speed.x - self.acceleration)
                if event.key == pygame.K_RIGHT:
                    speed.x = max(self.max_speed, speed.x + self.acceleration)
                if event.key == pygame.K_UP:
                    speed.y = min(-self.max_speed, speed.y - self.acceleration)
                if event.key == pygame.K_DOWN:
                    speed.y = max(self.max_speed, speed.y + self.acceleration)
        mod = speed.len()
        if mod > 0:
            speed.x = speed.x / mod * abs(speed.x)
            speed.y = speed.y / mod * abs(speed.y)
                    
class Space:
    def __init__(self, size, objs: dict={}):
        self.width, self.height = size
        self.objs = objs
        if objs:
            self.max_obj_id = max(objs.keys())
        else:
            self.max_obj_id = 0

    def append(self, obj):
        new_id = self.max_obj_id + 1
        self.objs[new_id] = obj
        self.max_obj_id = new_id
        return new_id
    
    def pop(self, obj_id):
        return self.objs.pop(obj_id)

    def update(self):
        lst_objs = self.objs.values()
        for obj in lst_objs:
            if obj.physbody:
                obj.physbody.update()                
        for obj_id, obj in self.objs.items():
            if obj.physbody:
                if not obj.physbody.is_update_collisions:
                    collisions = obj.collider.collisions(lst_objs)
                    obj.physbody.collisions(collisions)
                print(obj_id, obj.position, obj.physbody.speed)
                # input("Letter...")

    def main(self):
        while True:
            self.update()


class Camera:
    def __init__(self, space, screen, player):
        self.space= space
        self.screen = screen
        self.player = player

    def main(self):
        clock = pygame.time.Clock()
        running = True
        fps = FPS
        while running:
            self.screen.fill("black")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.player.handle_event(event)
            self.space.update()
            for obj in self.space.objs.values():
                if obj.name == "Player":
                    circle(self.screen, obj.position.x, obj.position.y, obj.collider.radius, color=(0, 0, 255))
                else:
                    circle(self.screen, obj.position.x, obj.position.y, obj.collider.radius)
            clock.tick(fps)
            pygame.display.flip()
        pygame.quit()
            
if __name__ == "__main__":
    
    objs = {
        1: GameObject(Vector2(-5, 0), Collider=CircleCollider, Physbody=Physbody, speed=Vector2(1, 0)),
        2: GameObject(Vector2(6, 5), Collider=CircleCollider, Physbody=Physbody, speed=Vector2(-1, 0)),
        3: GameObject(Vector2(4, 3), Collider=CircleCollider, Physbody=Physbody, speed=Vector2(-1, -1)),
        4: GameObject(Vector2(4, 4), Collider=CircleCollider, Physbody=Physbody, speed=Vector2(-1, -1)),
        5: GameObject(Vector2(5, 5), Collider=CircleCollider, Physbody=Physbody, speed=Vector2(-1, -1)),
        6: GameObject(Vector2(4, 6), Collider=CircleCollider, Physbody=Physbody, speed=Vector2(-1, -1)),
        7: GameObject(Vector2(4, 6), Collider=CircleCollider, Physbody=Physbody, speed=Vector2(-1, -1)),
        8: GameObject(Vector2(4, 6), Collider=CircleCollider, Physbody=Physbody, speed=Vector2(-1, -1)),
        9: GameObject(Vector2(4, 6), Collider=CircleCollider, Physbody=Physbody, speed=Vector2(-1, -1)),
    }
    space = Space((100, 100), objs)
    player = Player(Vector2(-5, 15))
    space.append(player)
    # for x in range(-20, 20, 2):
    #     for y in range(-4, 4, 2):
    #         obj = GameObject(Vector2(x, y), Collider=CircleCollider, 
    #                         Physbody=Physbody, speed=Vector2(y / 5, x / 25))
    #         space.append(obj)
    pygame.init()
    pygame.display.set_caption('Board')
    size = SX, SY
    screen = pygame.display.set_mode(size)

    camera = Camera(space, screen, player)
    camera.main()
    


