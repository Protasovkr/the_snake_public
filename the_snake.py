"""Игра «Изгиб Питона» — классическая «Змейка» на Pygame.

Змейка ползает по полю из ячеек, проходит сквозь стены, растёт, когда
съедает яблоко, и начинает заново, если укусит саму себя.
"""

from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центр поля, выровненный по сетке, — отсюда стартует змейка:
SCREEN_CENTER = (
    (GRID_WIDTH // 2) * GRID_SIZE,
    (GRID_HEIGHT // 2) * GRID_SIZE,
)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех объектов на игровом поле.

    Хранит общие атрибуты — позицию и цвет объекта — и объявляет
    метод draw, который дочерние классы переопределяют под себя.
    """

    def __init__(self, body_color=None):
        """Ставит объект в центр поля и задаёт его цвет."""
        self.position = SCREEN_CENTER
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на экране.

        Абстрактный метод: каждый дочерний класс переопределяет его.
        """
        pass

    def draw_cell(self, position):
        """Закрашивает одну ячейку цветом объекта и обводит её рамкой."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Яблоко — ячейка, которая появляется в случайном месте поля."""

    def __init__(self, body_color=APPLE_COLOR, occupied_positions=()):
        """Задаёт цвет яблока и ставит его в случайную свободную ячейку."""
        super().__init__(body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Перемещает яблоко в случайную ячейку игрового поля.

        Ячейки из occupied_positions (например, занятые змейкой)
        пропускаются, чтобы яблоко не появилось внутри змейки.
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка — список координат её сегментов.

    Голова — первый элемент списка positions. Класс отвечает за
    движение, рост, смену направления и отрисовку змейки.
    """

    def __init__(self, body_color=SNAKE_COLOR):
        """Создаёт змейку из одной головы в центре поля."""
        super().__init__(body_color)
        self.reset()
        # По правилам в начале игры змейка ползёт вправо:
        self.direction = RIGHT

    def reset(self):
        """Возвращает змейку в начальное состояние.

        Змейка снова состоит из одной головы в центре поля,
        а направление движения выбирается случайно.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Применяет направление, выбранное игроком, если оно есть."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Сдвигает змейку на одну ячейку в текущем направлении.

        В начало списка positions добавляется новая голова. Если змейка
        не выросла, последний сегмент удаляется и запоминается в last,
        чтобы метод draw затёр след. Уйдя за край поля, змейка
        появляется с противоположной стороны.
        """
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_head = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает змейку на экране и затирает её след.

        Сначала ячейка, которую покинул хвост, закрашивается цветом фона,
        затем рисуются все сегменты. Порядок важен: если голова заползла
        в только что освободившуюся ячейку, она не будет стёрта.
        """
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
        for position in self.positions:
            self.draw_cell(position)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и закрытие окна.

    Стрелки задают следующее направление движения змейки, развернуться
    назад нельзя. Закрытие окна завершает игру.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Создаёт игровые объекты и запускает основной игровой цикл."""
    # Инициализация PyGame:
    pygame.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Змейка съела яблоко: на следующем шаге она станет длиннее,
        # а яблоко появится в новой свободной ячейке.
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        # Змейка укусила себя: игра начинается заново.
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
