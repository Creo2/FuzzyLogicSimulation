from enum import Enum
class Color(Enum):
    BLACK = (0, 0, 0)
    GRAY = (150, 150, 150)
    LIGHTGRAY = (200, 200, 200)
    MEDGRAY = (175, 175, 175)
    WHITE = (255, 255, 255)
    RED = (150, 0, 0)
    GREEN = (100, 200, 100)
    DARKGREEN = (0, 100, 0)
    BLUE = (0, 0, 150)
    CYAN = (50, 220, 220)
    YELLOW = (220, 220, 50)

def get_colors():
    colors = [Color.RED,Color.GREEN,Color.CYAN,Color.BLUE,Color.DARKGREEN,Color.YELLOW,Color.BLACK,Color.GRAY]
    return colors
