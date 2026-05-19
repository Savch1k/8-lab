import tkinter as tk
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

# НАСЛЕДОВАНИЕ
# Все пользовательские исключения наследуются от базового класса SnakeGameError
# Это позволяет обрабатывать их все вместе через except SnakeGameError

class SnakeGameError(Exception):
    """Базовое исключение для игры Змейка - демонстрация наследования"""
    pass

class InvalidMoveError(SnakeGameError):  # ← НАСЛЕДОВАНИЕ от SnakeGameError
    """Исключение при неверном ходе"""
    pass

class GameOverError(SnakeGameError):     # ← НАСЛЕДОВАНИЕ от SnakeGameError
    """Исключение при завершении игры"""
    pass

class InvalidConfigurationError(SnakeGameError):  # ← НАСЛЕДОВАНИЕ
    """Исключение при некорректной конфигурации"""
    pass

#  КЛАССЫ И ИНКАПСУЛЯЦ

class Direction(Enum):
    """Класс-перечисление - пример простого класса с константами"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    
    # МЕТОД класса - определяет поведение объекта Direction
    def opposite(self) -> 'Direction':
        """МЕТОД: возвращает противоположное направление"""
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        return opposites[self]


@dataclass
class Point:
    """Data class - автоматически генерирует __init__, __eq__ и другие методы"""
    # АТРИБУТЫ (данные класса)
    x: int
    y: int
    
    # МЕТОД - перегрузка оператора + (полиморфизм)
    def __add__(self, other: 'Point') -> 'Point':
        """ПЕРЕГРУЗКА ОПЕРАТОРА: определяет поведение оператора + для точек"""
        return Point(self.x + other.x, self.y + other.y)
    
    # МЕТОД - перегрузка оператора == (полиморфизм)
    def __eq__(self, other: object) -> bool:
        """ПЕРЕГРУЗКА ОПЕРАТОРА: определяет сравнение точек"""
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y
    
    # МЕТОД - преобразование в другой тип
    def to_tuple(self) -> Tuple[int, int]:
        """МЕТОД: конвертирует точку в кортеж для удобства отрисовки"""
        return (self.x, self.y)


class Snake:
    """КЛАСС Змейка - инкапсулирует данные и методы для управления змейкой"""
    
    # КОНСТРУКТОР (специальный метод __init__) - создаёт объект
    def __init__(self, start_pos: Point, start_length: int = 3, direction: Direction = Direction.RIGHT):
        """
        КОНСТРУКТОР: инициализирует новый объект Snake
        Вызывается автоматически при создании экземпляра: snake = Snake(...)
        """
        # АТРИБУТЫ (инкапсулированные данные объекта)
        self._direction = direction  # _direction - защищённый атрибут (по convention)
        self._grow_pending = False   # инкапсуляция: состояние "нужно ли расти"
        self._body: List[Point] = []  # приватное поле для хранения тела
        
        # Валидация входных данных
        if start_length < 1:
            raise InvalidConfigurationError("Длина змейки должна быть не менее 1")
        
        # Создаём тело змейки
        for i in range(start_length):
            self._body.append(Point(start_pos.x - i, start_pos.y))
    
    # СВОЙСТВО (property) - геттер, позволяющий обращаться к _head как к атрибуту
    @property
    def head(self) -> Point:
        """
        ГЕТТЕР: свойство, возвращающее голову змейки.
        Используется как snake.head (без скобок), но внутри это метод.
        Пример полиморфизма: доступ к данным через метод, а не напрямую.
        """
        return self._body[0]
    
    @property
    def direction(self) -> Direction:
        """ГЕТТЕР: свойство для получения текущего направления"""
        return self._direction
    
    @property
    def body(self) -> List[Point]:
        """
        ГЕТТЕР: возвращает копию тела (инкапсуляция - защита от прямого изменения)
        Без этого метода внешний код мог бы изменить _body напрямую
        """
        return self._body.copy()  # возвращаем копию, чтобы нельзя было изменить оригинал
    
    # ПУБЛИЧНЫЙ МЕТОД - основной интерфейс взаимодействия со змейкой
    def change_direction(self, new_direction: Direction) -> None:
        """
        МЕТОД: изменяет направление движения с проверкой валидности
        Инкапсуляция: логика запрета разворота скрыта внутри метода
        """
        if new_direction == self._direction.opposite():
            # ГЕНЕРАЦИЯ ИСКЛЮЧЕНИЯ (собственный тип)
            raise InvalidMoveError("Нельзя повернуть на 180 градусов")
        self._direction = new_direction
    
    # ПУБЛИЧНЫЙ МЕТОД - основная логика движения
    def move(self) -> None:
        """
        МЕТОД: перемещает змейку в текущем направлении
        Инкапсулирует сложную логику: добавление головы, удаление хвоста, рост
        """
        # Вычисляем новую голову на основе текущего направления
        dx, dy = self._direction.value
        new_head = Point(self.head.x + dx, self.head.y + dy)
        
        # Вставляем новую голову в начало
        self._body.insert(0, new_head)
        
        # Если не нужно расти - удаляем хвост (игра "змейка")
        if not self._grow_pending:
            self._body.pop()
        else:
            self._grow_pending = False  # сбрасываем флаг после роста
    
    # ПУБЛИЧНЫЙ МЕТОД - изменение состояния
    def grow(self) -> None:
        """МЕТОД: отмечает, что змейка должна вырасти при следующем движении"""
        self._grow_pending = True
    
    # ПУБЛИЧНЫЙ МЕТОД - проверка состояния
    def check_self_collision(self) -> bool:
        """
        МЕТОД: проверяет, столкнулась ли голова с телом
        Возвращает bool - пример метода-предиката
        """
        return self.head in self._body[1:]  # исключаем голову из проверки
    
    # ПУБЛИЧНЫЙ МЕТОД - получение данных для отрисовки
    def get_body_positions(self) -> List[Tuple[int, int]]:
        """
        МЕТОД: возвращает все позиции тела в формате, удобном для GUI
        Адаптер/преобразователь данных (паттерн Adapter)
        """
        return [point.to_tuple() for point in self._body]


class Food:
    """КЛАСС Еда - инкапсулирует логику появления еды"""
    
    # КОНСТРУКТОР
    def __init__(self, width: int, height: int, snake: Snake):
        """
        КОНСТРУКТОР: создаёт еду, учитывая позицию змейки
        Композиция: Food содержит ссылку на Snake (знает о существовании змейки)
        """
        self._width = width
        self._height = height
        self._position = self._randomize_position(snake)  # вызов приватного метода
    
    # ПРИВАТНЫЙ МЕТОД (по convention - начинается с _)
    def _randomize_position(self, snake: Snake) -> Point:
        """
        ПРИВАТНЫЙ МЕТОД: генерирует случайную позицию, не занятую змейкой
        Инкапсуляция: детали генерации скрыты от внешнего мира
        """
        max_attempts = self._width * self._height * 2
        for _ in range(max_attempts):
            x = random.randint(0, self._width - 1)
            y = random.randint(0, self._height - 1)
            candidate = Point(x, y)
            if candidate not in snake.body:  # используем геттер snake.body
                return candidate
        
        # Если свободных мест нет - победа!
        raise GameOverError("Победа! Всё поле заполнено!")
    
    # СВОЙСТВО (property) - геттер
    @property
    def position(self) -> Point:
        """ГЕТТЕР: возвращает позицию еды (только для чтения)"""
        return self._position
    
    # ПУБЛИЧНЫЙ МЕТОД - изменение состояния
    def respawn(self, snake: Snake) -> None:
        """
        МЕТОД: перемещает еду на новое место после съедания
        Пример метода, изменяющего состояние объекта
        """
        self._position = self._randomize_position(snake)
    
    # ПУБЛИЧНЫЙ МЕТОД - проверка коллизии
    def check_collision(self, point: Point) -> bool:
        """
        МЕТОД: проверяет, съела ли змейка еду
        Использует перегруженный оператор == класса Point (полиморфизм)
        """
        return self._position == point  # неявный вызов Point.__eq__


class SnakeGame:
    """
    КЛАСС ИГРОВОЙ ДВИЖОК
    Композиция: содержит объекты Snake и Food (управляет ими)
    Агрегация: управляет их взаимодействием
    """
    
    # КОНСТРУКТОР
    def __init__(self, width: int = 20, height: int = 15, cell_size: int = 30):
        """КОНСТРУКТОР: инициализирует все компоненты игры"""
        # Валидация
        if width < 5 or height < 5:
            raise InvalidConfigurationError("Размеры поля должны быть не менее 5x5")
        
        # АТРИБУТЫ (состояние игры)
        self._width = width
        self._height = height
        self._cell_size = cell_size
        self._score = 0
        self._game_over = False
        self._won = False
        self._timer_id = None  # для хранения ID таймера tkinter
        
        # КОМПОЗИЦИЯ: создаём объекты внутри конструктора
        # SnakeGame ВЛАДЕЕТ объектами Snake и Food (жёсткая связь)
        start_pos = Point(width // 2, height // 2)
        self._snake = Snake(start_pos, start_length=3)
        self._food = Food(width, height, self._snake)
    
    # СВОЙСТВА (геттеры) - инкапсуляция данных
    @property
    def score(self) -> int:
        """ГЕТТЕР: получение счёта (только чтение)"""
        return self._score
    
    @property
    def game_over(self) -> bool:
        """ГЕТТЕР: статус окончания игры"""
        return self._game_over
    
    @property
    def won(self) -> bool:
        """ГЕТТЕР: статус победы"""
        return self._won
    
    @property
    def snake(self) -> Snake:
        """ГЕТТЕР: доступ к змейке (для GUI)"""
        return self._snake
    
    @property
    def food(self) -> Food:
        """ГЕТТЕР: доступ к еде (для GUI)"""
        return self._food
    
    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def cell_size(self) -> int:
        return self._cell_size
    
    @property
    def timer_id(self) -> Optional[str]:
        return self._timer_id
    
    @timer_id.setter
    def timer_id(self, value: Optional[str]) -> None:
        """СЕТТЕР: позволяет изменять timer_id (контролируемый доступ)"""
        self._timer_id = value
    
    # ПУБЛИЧНЫЙ МЕТОД - основной игровой цикл
    def update(self) -> bool:
        """
        МЕТОД: обновляет состояние игры на один кадр
        Возвращает False, если игра окончена (пример метода с возвратом значения)
        """
        if self._game_over:
            return False
        
        try:
            # ДЕЛЕГИРОВАНИЕ: вызываем методы вложенных объектов
            self._snake.move()
            
            # Проверка столкновения с собой
            if self._snake.check_self_collision():
                self._game_over = True
                self._won = False
                return False
            
            # Проверка столкновения со стенами
            head = self._snake.head
            if head.x < 0 or head.x >= self._width or head.y < 0 or head.y >= self._height:
                self._game_over = True
                self._won = False
                return False
            
            # Проверка поедания еды (ПОЛИМОРФИЗМ: объект еды сам знает, как проверять)
            if self._food.check_collision(head):
                self._score += 10
                self._snake.grow()  # вызываем метод snake
                try:
                    self._food.respawn(self._snake)  # вызываем метод food
                except GameOverError:
                    # Победа - всё поле заполнено
                    self._game_over = True
                    self._won = True
                    return False
            
            return True
            
        except Exception as e:
            # Обработка исключений (в том числе пользовательских)
            self._game_over = True
            self._won = False
            raise SnakeGameError(f"Ошибка в игровом процессе: {e}")
    
    # ПУБЛИЧНЫЙ МЕТОД - делегирование команды
    def change_direction(self, direction: Direction) -> None:
        """
        МЕТОД: изменяет направление змейки
        Паттерн "Делегирование" - передаёт вызов соответствующему объекту
        """
        if not self._game_over:
            try:
                self._snake.change_direction(direction)
            except InvalidMoveError:
                # Игнорируем недопустимый поворот (инкапсуляция обработки ошибки)
                pass


class SnakeGUI:
    """
    КЛАСС ГРАФИЧЕСКОГО ИНТЕРФЕЙСА
    Отделяет логику игры от отображения (MVC: View + Controller)
    """
    
    # КЛАССОВЫЕ АТРИБУТЫ (общие для всех экземпляров)
    COLORS = {
        'bg': '#1a1a2e',
        'snake_head': '#16213e',
        'snake_body': '#0f3460',
        'food': '#e94560',
        'wall': '#533483',
        'text': '#eeeeee'
    }
    
    # КОНСТРУКТОР
    def __init__(self, width: int = 20, height: int = 15, cell_size: int = 30):
        """КОНСТРУКТОР: создаёт окно и все GUI-компоненты"""
        # КОМПОЗИЦИЯ: GUI создаёт и содержит игровой движок
        self._root = tk.Tk()
        self._root.title("🐍 Змейка")
        self._root.resizable(False, False)
        self._root.configure(bg=self.COLORS['bg'])
        
        # АТРИБУТЫ
        self._width = width
        self._height = height
        self._cell_size = cell_size
        self._game_speed = 150
        self._running = True
        
        # СОЗДАНИЕ ИГРОВОГО ДВИЖКА (композиция)
        try:
            self._game = SnakeGame(width, height, cell_size)
        except InvalidConfigurationError as e:
            tk.messagebox.showerror("Ошибка конфигурации", str(e))
            self._root.destroy()
            return
        
        # ВЫЗОВЫ ДРУГИХ МЕТОДОВ (приватных)
        self._create_widgets()
        self._bind_keys()
        
        # ЗАПУСК ИГРОВОГО ЦИКЛА
        self._game_loop()
    
    # ПРИВАТНЫЙ МЕТОД (для внутреннего использования)
    def _create_widgets(self) -> None:
        """ПРИВАТНЫЙ МЕТОД: создаёт все элементы GUI"""
        canvas_width = self._width * self._cell_size
        canvas_height = self._height * self._cell_size
        
        self._canvas = tk.Canvas(
            self._root,
            width=canvas_width,
            height=canvas_height,
            bg=self.COLORS['bg'],
            highlightthickness=0
        )
        self._canvas.pack(pady=10)
        
        # Панель информации
        info_frame = tk.Frame(self._root, bg=self.COLORS['bg'])
        info_frame.pack(pady=5)
        
        self._score_label = tk.Label(
            info_frame,
            text=f"Счёт: {self._game.score}",  # используем property score
            font=('Arial', 14, 'bold'),
            fg=self.COLORS['text'],
            bg=self.COLORS['bg']
        )
        self._score_label.pack(side=tk.LEFT, padx=20)
        
        # Кнопка рестарта с ЛЯМБДА-ФУНКЦИЕЙ (callback)
        self._restart_btn = tk.Button(
            info_frame,
            text="🔄 Новая игра",
            font=('Arial', 10),
            command=lambda: self._restart_game(),  # лямбда как замыкание
            bg=self.COLORS['food'],
            fg='white',
            cursor='hand2'
        )
        self._restart_btn.pack(side=tk.RIGHT, padx=20)
        
        self._status_label = tk.Label(
            self._root,
            text="Используйте стрелки для управления",
            font=('Arial', 10),
            fg=self.COLORS['text'],
            bg=self.COLORS['bg']
        )
        self._status_label.pack(pady=5)
    
    # ПРИВАТНЫЙ МЕТОД
    def _bind_keys(self) -> None:
        """ПРИВАТНЫЙ МЕТОД: привязывает клавиши управления"""
        key_bindings = {
            '<Up>': Direction.UP,
            '<Down>': Direction.DOWN,
            '<Left>': Direction.LEFT,
            '<Right>': Direction.RIGHT,
            'w': Direction.UP,
            's': Direction.DOWN,
            'a': Direction.LEFT,
            'd': Direction.RIGHT
        }
        
        for key, direction in key_bindings.items():
            # ЛЯМБДА внутри цикла с замыканием (сохраняет значение direction)
            self._root.bind(key, lambda e, d=direction: self._game.change_direction(d))
        
        self._root.bind('<r>', lambda e: self._restart_game())
        self._root.bind('<R>', lambda e: self._restart_game())
        self._root.bind('<p>', lambda e: self._toggle_pause())
        self._root.bind('<P>', lambda e: self._toggle_pause())
    
    # ПУБЛИЧНЫЙ МЕТОД (вызывается из GUI)
    def _toggle_pause(self) -> None:
        """МЕТОД: приостанавливает или возобновляет игру"""
        if self._game.game_over:
            return
        
        self._running = not self._running
        if self._running:
            self._status_label.config(text="Игра продолжается...")
            self._game_loop()  # рекурсивный вызов
        else:
            self._status_label.config(text="⏸ ПАУЗА. Нажмите P для продолжения")
    
    # ПУБЛИЧНЫЙ МЕТОД
    def _restart_game(self) -> None:
        """МЕТОД: перезапускает игру"""
        self._running = False
        if hasattr(self, '_game') and self._game.timer_id:
            self._root.after_cancel(self._game.timer_id)
        
        # СОЗДАНИЕ НОВОГО ОБЪЕКТА (демонстрация жизненного цикла)
        try:
            self._game = SnakeGame(self._width, self._height, self._cell_size)
        except InvalidConfigurationError as e:
            tk.messagebox.showerror("Ошибка конфигурации", str(e))
            return
        
        self._running = True
        self._game_speed = 150
        self._score_label.config(text="Счёт: 0")
        self._status_label.config(text="Используйте стрелки для управления")
        self._game_loop()
    
    # ПРИВАТНЫЙ МЕТОД ОТРИСОВКИ
    def _draw_grid(self) -> None:
        """ПРИВАТНЫЙ МЕТОД: рисует сетку игрового поля"""
        for i in range(self._width):
            for j in range(self._height):
                x1 = i * self._cell_size
                y1 = j * self._cell_size
                x2 = x1 + self._cell_size
                y2 = y1 + self._cell_size
                
                fill = '#16213e' if (i + j) % 2 == 0 else '#1a1a2e'
                self._canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline='#0f3460')
    
    # ПРИВАТНЫЙ МЕТОД ОТРИСОВКИ
    def _draw_snake(self) -> None:
        """ПРИВАТНЫЙ МЕТОД: рисует змейку, используя данные из game.snake"""
        # ПОЛИМОРФИЗМ: вызываем метод get_body_positions() у snake
        body_positions = self._game.snake.get_body_positions()
        
        for i, (x, y) in enumerate(body_positions):
            x1 = x * self._cell_size
            y1 = y * self._cell_size
            x2 = x1 + self._cell_size
            y2 = y1 + self._cell_size
            
            fill = '#00adb5' if i == 0 else self.COLORS['snake_body']
            outline = '#00fff5' if i == 0 else '#1f6e8c'
            
            self._canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=1)
            
            # Рисуем глаза на голове
            if i == 0:
                self._draw_eyes(x1, y1)
    
    # ПРИВАТНЫЙ МЕТОД - декомпозиция (разбиение сложного метода)
    def _draw_eyes(self, x1: int, y1: int) -> None:
        """ПРИВАТНЫЙ МЕТОД: рисует глаза змейки в зависимости от направления"""
        eye_size = self._cell_size // 6
        eye_offset = self._cell_size // 3
        direction = self._game.snake.direction  # используем property
        
        if direction == Direction.RIGHT:
            eyes_x = [x1 + self._cell_size - eye_offset, x1 + self._cell_size - eye_offset]
            eyes_y = [y1 + eye_offset, y1 + self._cell_size - eye_offset]
        elif direction == Direction.LEFT:
            eyes_x = [x1 + eye_offset, x1 + eye_offset]
            eyes_y = [y1 + eye_offset, y1 + self._cell_size - eye_offset]
        elif direction == Direction.UP:
            eyes_x = [x1 + eye_offset, x1 + self._cell_size - eye_offset]
            eyes_y = [y1 + eye_offset, y1 + eye_offset]
        else:  # DOWN
            eyes_x = [x1 + eye_offset, x1 + self._cell_size - eye_offset]
            eyes_y = [y1 + self._cell_size - eye_offset, y1 + self._cell_size - eye_offset]
        
        for ex, ey in zip(eyes_x, eyes_y):
            self._canvas.create_oval(ex, ey, ex + eye_size, ey + eye_size, fill='white', outline='')
    
    # ПРИВАТНЫЙ МЕТОД ОТРИСОВКИ
    def _draw_food(self) -> None:
        """ПРИВАТНЫЙ МЕТОД: рисует еду, используя данные из game.food"""
        x, y = self._game.food.position.to_tuple()  # цепочка вызовов
        x1 = x * self._cell_size
        y1 = y * self._cell_size
        x2 = x1 + self._cell_size
        y2 = y1 + self._cell_size
        
        margin = self._cell_size // 6
        self._canvas.create_oval(
            x1 + margin, y1 + margin,
            x2 - margin, y2 - margin,
            fill=self.COLORS['food'],
            outline='#ff7b89',
            width=1
        )
        
        center_margin = self._cell_size // 3
        self._canvas.create_oval(
            x1 + center_margin, y1 + center_margin,
            x2 - center_margin, y2 - center_margin,
            fill='#ff2e63',
            outline=''
        )
    
    # ПРИВАТНЫЙ МЕТОД
    def _draw_game_over(self) -> None:
        """ПРИВАТНЫЙ МЕТОД: рисует экран окончания игры"""
        self._canvas.create_rectangle(
            0, 0,
            self._width * self._cell_size,
            self._height * self._cell_size,
            fill='black',
            stipple='gray50'
        )
        
        text = "🎉 ПОБЕДА! 🎉" if self._game.won else "💀 ИГРА ОКОНЧЕНА 💀"
        subtext = f"Финальный счёт: {self._game.score}"
        
        self._canvas.create_text(
            self._width * self._cell_size // 2,
            self._height * self._cell_size // 2 - 20,
            text=text,
            font=('Arial', 18, 'bold'),
            fill=self.COLORS['food']
        )
        
        self._canvas.create_text(
            self._width * self._cell_size // 2,
            self._height * self._cell_size // 2 + 20,
            text=subtext,
            font=('Arial', 12),
            fill=self.COLORS['text']
        )
        
        self._canvas.create_text(
            self._width * self._cell_size // 2,
            self._height * self._cell_size // 2 + 50,
            text="Нажмите R для новой игры",
            font=('Arial', 10),
            fill=self.COLORS['text']
        )
    
    # ПРИВАТНЫЙ МЕТОД
    def _update_display(self) -> None:
        """ПРИВАТНЫЙ МЕТОД: обновляет всё отображение на канвасе"""
        self._canvas.delete('all')
        self._draw_grid()
        self._draw_food()
        self._draw_snake()
        self._score_label.config(text=f"Счёт: {self._game.score}")
        
        if self._game.game_over:
            self._draw_game_over()
    
    # ПУБЛИЧНЫЙ МЕТОД - ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ
    def _game_loop(self) -> None:
        """
        МЕТОД: основной игровой цикл (рекурсивный вызов через after)
        Рекурсия с задержкой - типичный паттерн в GUI-играх
        """
        if not self._running:
            return
        
        if not self._game.game_over:
            try:
                # ВЫЗОВ МЕТОДА update() у игрового движка
                self._game.update()
                self._update_display()
                
                # Динамическое изменение скорости (полиморфизм поведения)
                new_speed = max(80, 150 - (self._game.score // 10) * 2)
                if new_speed != self._game_speed:
                    self._game_speed = new_speed
                
                # РЕКУРСИВНЫЙ ВЫЗОВ (с задержкой)
                self._game.timer_id = self._root.after(self._game_speed, self._game_loop)
                
            except SnakeGameError as e:  # Обработка пользовательского исключения
                self._game._game_over = True
                self._update_display()
                tk.messagebox.showerror("Ошибка", str(e))
        else:
            self._update_display()
    
    # ПУБЛИЧНЫЙ МЕТОД - точка входа для запуска
    def run(self) -> None:
        """ПУБЛИЧНЫЙ МЕТОД: запускает главный цикл tkinter"""
        self._root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._root.mainloop()  # блокирующий вызов tkinter
    
    # ПРИВАТНЫЙ МЕТОД - обработчик закрытия окна
    def _on_closing(self) -> None:
        """ПРИВАТНЫЙ МЕТОД: корректно завершает игру при закрытии окна"""
        if hasattr(self._game, 'timer_id') and self._game.timer_id:
            self._root.after_cancel(self._game.timer_id)
        self._root.destroy()

def main():
    try:
        # СОЗДАНИЕ ОБЪЕКТА (вызов конструктора)
        app = SnakeGUI(width=20, height=15, cell_size=30)
        # ВЫЗОВ МЕТОДА ОБЪЕКТА
        app.run()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()