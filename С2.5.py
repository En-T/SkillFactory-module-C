from random import randint


class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Board:
    def __init__(self, size=6, hid=False):
        self.size = size
        self.field_us = [[" "]*self.size for _ in range(self.size)]
        self.field_ai = [[" "]*self.size for _ in range(self.size)]
        self.ships_us = []
        self.ships_ai = []
        self.busy_us = []
        self.busy_ai = []        

    def __str__(self):
        res = " " * 5
        res += ("Доска пользователя")
        res += " " * 14
        res += ("Доска компьютера\n")
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        res += " " * 5
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |\n"
        res += "-" * 27
        res += " " * 5
        res += "-" * 27
        for row_us, row_ai in zip(enumerate(self.field_us), enumerate(self.field_ai)):
            res += f"\n{row_us[0]+1} | " + " | ".join(row_us[1]) + " |"
            res += " " * 5 
            for i, elem in enumerate(row_ai[1]):
                if elem == "█":
                    row_ai[1][i] = " "
            res += f"{row_ai[0]+1} | " + " | ".join(row_ai[1]) + " |\n"
            res += "-" * 27
            res += " " * 5
            res += "-" * 27 
        return res

    def out(self, d):
        return not((0 <= d[0] < self.size) and (0 <= d[1] < self.size))

    def contour(self, ship, field, busy, verb=False):
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for d in ship:          
            for dx, dy in near:
                cur = (d[0] + dx, d[1] + dy)                
                if not(self.out(cur)) and cur not in busy:                    
                    if verb:                        
                        field[cur[0]][cur[1]] = "*"
                    else:
                        field[cur[0]][cur[1]] = " "                    
                    busy.append(cur)        

    def add_ship(self, ship, field, ships, busy): 
        for d in ship:            
            if self.out(d) or d in busy:
                raise BoardWrongShipException()        
        for d in ship:                            
            field[d[0]][d[1]] = "█"
            busy.append(d)
        ships.append(ship)
        self.contour(ship, field, busy) 

    def shot(self, d, field, ships, busy, lens):
        if self.out(d):
            raise BoardOutException()        
        if d in busy:
            raise BoardUsedException()        
        busy.append(d)        
        for ship in ships:
            if d in ship:
                lens[ships.index(ship)] -= 1
                field[d[0]][d[1]] = "X"
                if lens[ships.index(ship)] == 0:
                    self.contour(ship, field, busy, verb = True)
                    print("Корабль уничтожен!")                    
                    return True
                else:
                    print("Корабль ранен!")
                    return False        
        field[d[0]][d[1]] = "*"
        print("Мимо!")
        return True   

class Ship:
    def __init__(self, prow, l, o):
        self.prow = prow
        self.l = l
        self.o = o
    
    def dots(self):
        ship_dots = []
        cur_x, cur_y = self.prow[0], self.prow[1]
        ship_dots.append((cur_x, cur_y))
        for i in range(self.l - 1):
            if self.o == 0:
                cur_y += 1
            if self.o == 1:
                cur_x += 1
            ship_dots.append((cur_x, cur_y))
        return ship_dots

class Games:
    def __init__(self, size = 6):
        self.board = Board()
        self.size = size 
        self.lens_us = [3, 2, 2, 1, 1, 1, 1]
        self.lens_ai = [3, 2, 2, 1, 1, 1, 1]               

    def random_board(self, field, ships, busy):
        board = None
        while board is None:             
            board = self.random_ship(field, ships, busy) 
            ships = [] 
            busy = []                         
        return board

    def random_ship(self, field, ships, busy):
        attempts = 0
        for l in self.lens_us:
            while True:
                attempts += 1
                if attempts > 2000:                                       
                    return None
                ship = Ship((randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    self.board.add_ship(ship.dots(), field, ships, busy)
                    break
                except BoardWrongShipException:
                    pass
        self.begin()
        return self.board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def begin(self):
        self.board.busy_us = []
        self.board.busy_ai = []

    def start(self):
        self.greet()
        self.random_board(self.board.field_us, self.board.ships_us, self.board.busy_us)           
        self.random_board(self.board.field_ai, self.board.ships_ai, self.board.busy_ai)
        self.loop()

    def ask_us(self):
        while True:
            cords = input("Ваш ход: ").split()
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue   
            x, y = cords
            if not(x.isdigit()) or not(y.isdigit()):
                print(" Введите числа! ")
                continue            
            break        
        return (int(x) - 1, int(y) - 1)

    def ask_ai(self):
        x, y = randint(0, self.size - 1), randint(0, self.size - 1)
        print(f"Ход компьютера: {x + 1} {y + 1}")
        return (int(x), int(y))

    def check_win(self, lens, str):
        if set(lens) == {0}:
            print(str, " победил!!!")
            return True

    def loop(self):
        while True:                            
                while True:
                    try:
                        print(self.board)
                        if self.board.shot(self.ask_us(), self.board.field_ai, self.board.ships_ai, self.board.busy_us, self.lens_us):
                            break
                    except BoardException as e:
                        print(e)
                if self.check_win(self.lens_us, "Игрок"):
                    break
                    
                while True:
                    try:
                        print(self.board)
                        if self.board.shot(self.ask_ai(), self.board.field_us, self.board.ships_us, self.board.busy_ai, self.lens_ai):
                            break
                    except BoardException as e:
                        print(e)
                if self.check_win(self.lens_ai, "Компьютер"):
                    break                            
        print(self.board)           
        

g = Games()
g.start()