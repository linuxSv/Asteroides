import pygame
import random
import json
import os

# Obtener la ruta de la carpeta actual
current_folder = os.path.dirname(__file__)

# Inicializar pygame
pygame.init()

# Configuración de la pantalla
screen_width = 960
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Asteroides Mejorado")

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

# Fuente para el texto
font = pygame.font.Font(None, 36)

# Cargar sonidos desde la carpeta actual
pygame.mixer.init()
shoot_sound = pygame.mixer.Sound(os.path.join(current_folder, "shoot.mp3"))  # Sonido de disparo
explosion_sound = pygame.mixer.Sound(os.path.join(current_folder, "explosion.mp3"))  # Sonido de explosión
pygame.mixer.music.load(os.path.join(current_folder, "arcade.mp3"))  # Música de fondo
pygame.mixer.music.play(-1)  # Repetir música en bucle

# Clase para la nave
class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([20, 20], pygame.SRCALPHA)  # Superficie transparente
        pygame.draw.polygon(self.image, WHITE, [(10, 0), (0, 20), (20, 20)])  # Triángulo
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height // 2)
        self.speed = 5
        self.lives = 3  # Vidas de la nave

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        # Mantener la nave dentro de la pantalla
        self.rect.x = max(0, min(self.rect.x, screen_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, screen_height - self.rect.height))

# Clase para los asteroides
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, size, x=None, y=None):
        super().__init__()
        self.size = size
        self.image = pygame.Surface([size * 2, size * 2], pygame.SRCALPHA)  # Superficie transparente
        self.color = random.choice(COLORS)  # Color aleatorio
        pygame.draw.circle(self.image, self.color, (size, size), size)  # Círculo
        self.rect = self.image.get_rect()
        if x is None and y is None:
            self.rect.x = random.randrange(screen_width - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
        else:
            self.rect.center = (x, y)
        self.speed_y = random.randrange(1, 4)
        self.speed_x = random.randrange(-2, 2)

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.top > screen_height + 10 or self.rect.left < -25 or self.rect.right > screen_width + 20:
            self.kill()  # Eliminar el asteroide si sale de la pantalla

    def split(self):
        """Dividir el asteroide en dos más pequeños."""
        if self.size > 10:  # Solo dividir si el tamaño es mayor que 10
            for _ in range(2):
                new_asteroid = Asteroid(self.size // 2, self.rect.centerx, self.rect.centery)
                all_sprites.add(new_asteroid)
                asteroids.add(new_asteroid)

# Clase para los disparos
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([4, 10], pygame.SRCALPHA)  # Superficie transparente
        pygame.draw.rect(self.image, GREEN, [0, 0, 4, 10])  # Línea vertical
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10  # Disparo hacia arriba

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:  # Eliminar el disparo si sale de la pantalla
            self.kill()

# Clase para las partículas
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface([4, 4], pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (2, 2), 2)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = random.randrange(-3, 3)
        self.speed_y = random.randrange(-3, 3)
        self.lifetime = 30  # Duración de la partícula

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

# Función para cargar la tabla de puntuaciones
def load_high_scores():
    try:
        with open(os.path.join(current_folder, "high_scores.json"), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Función para guardar la tabla de puntuaciones
def save_high_scores(scores):
    with open(os.path.join(current_folder, "high_scores.json"), "w") as file:
        json.dump(scores, file)

# Función para mostrar la tabla de puntuaciones
def show_high_scores(screen, scores):
    screen.fill(BLACK)
    title_text = font.render("Mejores Puntuaciones", True, WHITE)
    screen.blit(title_text, (screen_width // 2 - 150, 50))

    y_offset = 150
    for i, score in enumerate(scores[:10]):  # Mostrar solo los 10 mejores
        score_text = font.render(f"{i + 1}. {score['name']}: {score['score']}", True, WHITE)
        screen.blit(score_text, (screen_width // 2 - 100, y_offset))
        y_offset += 50

    pygame.display.flip()

# Crear grupos de sprites
all_sprites = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
bullets = pygame.sprite.Group()
particles = pygame.sprite.Group()

# Crear la nave
ship = Ship()
all_sprites.add(ship)

# Crear asteroides iniciales
for i in range(5):
    asteroid = Asteroid(random.randint(20, 40))
    all_sprites.add(asteroid)
    asteroids.add(asteroid)

# Puntuación
score = 0

# Reloj para controlar la velocidad de actualización
clock = pygame.time.Clock()

# Bucle principal del juego
running = True
game_over = False
asteroid_spawn_time = 0  # Tiempo para generar nuevos asteroides
high_scores = load_high_scores()

while running:
    # Mantener el bucle funcionando a la velocidad correcta
    clock.tick(60)

    # Procesar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:  # Disparar con la barra espaciadora
                bullet = Bullet(ship.rect.centerx, ship.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()  # Reproducir sonido de disparo

    if not game_over:
        # Actualizar
        all_sprites.update()
        particles.update()

        # Generar nuevos asteroides continuamente
        asteroid_spawn_time += 1
        if asteroid_spawn_time >= 60:  # Generar un asteroide cada segundo (60 frames)
            asteroid = Asteroid(random.randint(20, 40))
            all_sprites.add(asteroid)
            asteroids.add(asteroid)
            asteroid_spawn_time = 0

        # Verificar colisiones entre disparos y asteroides
        for bullet in bullets:
            asteroid_hit_list = pygame.sprite.spritecollide(bullet, asteroids, True)
            for asteroid in asteroid_hit_list:
                bullet.kill()
                score += 10  # Aumentar puntuación
                asteroid.split()  # Dividir el asteroide
                explosion_sound.play()  # Reproducir sonido de explosión
                # Crear partículas
                for _ in range(10):
                    particle = Particle(asteroid.rect.centerx, asteroid.rect.centery, asteroid.color)
                    particles.add(particle)
                    all_sprites.add(particle)

        # Verificar colisiones entre la nave y los asteroides
        if pygame.sprite.spritecollide(ship, asteroids, False):
            ship.lives -= 1  # Perder una vida
            if ship.lives <= 0:
                game_over = True
                # Guardar puntuación si es alta
                if len(high_scores) < 10 or score > high_scores[-1]["score"]:
                    name = input("Ingresa tu nombre: ")  # Pedir nombre al jugador
                    high_scores.append({"name": name, "score": score})
                    high_scores.sort(key=lambda x: x["score"], reverse=True)
                    save_high_scores(high_scores)
            else:
                # Reiniciar posición de la nave
                ship.rect.center = (screen_width // 2, screen_height // 2)

    # Dibujar / renderizar
    screen.fill(BLACK)
    all_sprites.draw(screen)
    particles.draw(screen)

    # Mostrar puntuación
    score_text = font.render(f"Puntuación: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Mostrar vidas
    lives_text = font.render(f"Vidas: {ship.lives}", True, WHITE)
    screen.blit(lives_text, (screen_width - 150, 10))

    # Mostrar "Juego Terminado" si es necesario
    if game_over:
        game_over_text = font.render("Juego Terminado", True, WHITE)
        screen.blit(game_over_text, (screen_width // 2 - 100, screen_height // 2))
        restart_text = font.render("Presiona R para jugar de nuevo", True, WHITE)
        screen.blit(restart_text, (screen_width // 2 - 150, screen_height // 2 + 50))

        # Verificar si el jugador presiona R para reiniciar
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            # Reiniciar el juego
            game_over = False
            ship.lives = 3
            score = 0
            all_sprites.empty()
            asteroids.empty()
            bullets.empty()
            particles.empty()
            ship = Ship()
            all_sprites.add(ship)
            for i in range(5):
                asteroid = Asteroid(random.randint(20, 40))
                all_sprites.add(asteroid)
                asteroids.add(asteroid)

    # Actualizar la pantalla
    pygame.display.flip()

# Salir del juego
pygame.quit()
