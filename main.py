import math
import sys
import pygame
import queue
import random
import copy
import timeit

pygame.init()

running = True
window = True
############### WINDOW #######################################
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Snake")
fps = pygame.time.Clock()
game_over = False
# icon = pygame.image.load('way.png')
# pygame.display.set_icon(icon)

###############################################################
# PriorityQueue Ordering
class Prioritize:
    def __init__(self, priority, item):
        self.priority = priority
        self.item = item

    def __eq__(self, other):
        return self.priority == other.priority

    def __lt__(self, other):
        return self.priority < other.priority


snakeLocation = [(40, 40), (41, 40), (42, 40)]
global appleLocationX
global appleLocationY

class GridObj(object):
    def __init__(self):
        self.cols = 80
        self.grid = [0 for i in range(self.cols)]
        self.row = 80
        self.grass = (25, 255, 102)
        self.apple = (255, 255, 0)  #yellow
        self.snakeBody = (255, 0, 0)
        self.snakeHead = (179, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.grey = (220, 220, 220)
        self.width = 800 / self.cols
        self.height = 800 / self.row

    def createPlayGround(self):
        # create 2d array
        for i in range(self.cols):
            self.grid[i] = [0 for i in range(self.row)]

        # Create Spots
        for i in range(self.cols):
            for j in range(self.row):
                self.grid[i][j] = SearchBlock((i, j), None, 0, 1)

        for i in range(self.cols):
            for j in range(self.row):
                self.grid[i][j].show(self, self.grass, 0)

        for i in range(0, self.row):
            self.grid[0][i].show(self, self.grey, 0)
            self.grid[0][i].obs = True
            self.grid[self.cols - 1][i].obs = True
            self.grid[self.cols - 1][i].show(self, self.grey, 0)
            self.grid[i][self.row - 1].show(self, self.grey, 0)
            self.grid[i][0].show(self, self.grey, 0)
            self.grid[i][0].obs = True
            self.grid[i][self.row - 1].obs = True

    def moveLeft(self):
        if len(snakeLocation) > 1:
            if ((snakeLocation[0][0]) - 1) != (snakeLocation[1][0]):
                if self.grid[snakeLocation[0][0] - 1][snakeLocation[0][1]].obs is False:
                    clearOldSnakeLocation(self)

                    oldSnakeLocation = list(snakeLocation)
                    snakeLocation[0] = (snakeLocation[0][0] - 1, snakeLocation[0][1])
                    for bodyIdx in range(1, len(snakeLocation)):
                        snakeLocation[bodyIdx] = (oldSnakeLocation[bodyIdx-1][0], oldSnakeLocation[bodyIdx-1][1])
                    updateSnake(self)

    def moveRight(self):
        if len(snakeLocation) > 1:
            if ((snakeLocation[0][0]) + 1) != (snakeLocation[1][0]):
                if self.grid[snakeLocation[0][0] + 1][snakeLocation[0][1]].obs is False:
                    clearOldSnakeLocation(self)

                    oldSnakeLocation = list(snakeLocation)
                    snakeLocation[0] = (snakeLocation[0][0] + 1, snakeLocation[0][1])
                    for bodyIdx in range(1, len(snakeLocation)):
                        snakeLocation[bodyIdx] = (oldSnakeLocation[bodyIdx - 1][0], oldSnakeLocation[bodyIdx - 1][1])
                    updateSnake(self)

    def moveUp(self):
        if len(snakeLocation) > 1:
            if ((snakeLocation[0][1]) - 1) != (snakeLocation[1][1]):
                if self.grid[snakeLocation[0][0]][snakeLocation[0][1] - 1].obs is False:
                    clearOldSnakeLocation(self)

                    oldSnakeLocation = list(snakeLocation)
                    snakeLocation[0] = (snakeLocation[0][0], snakeLocation[0][1] - 1)
                    for bodyIdx in range(1, len(snakeLocation)):
                        snakeLocation[bodyIdx] = (oldSnakeLocation[bodyIdx - 1][0], oldSnakeLocation[bodyIdx - 1][1])
                    updateSnake(self)

    def moveDown(self):
        if len(snakeLocation) > 1:
            if ((snakeLocation[0][1]) + 1) != (snakeLocation[1][1]):
                if self.grid[snakeLocation[0][0]][snakeLocation[0][1] + 1].obs is False:
                    clearOldSnakeLocation(self)

                    oldSnakeLocation = list(snakeLocation)
                    snakeLocation[0] = (snakeLocation[0][0], snakeLocation[0][1] + 1)
                    for bodyIdx in range(1, len(snakeLocation)):
                        snakeLocation[bodyIdx] = (oldSnakeLocation[bodyIdx - 1][0], oldSnakeLocation[bodyIdx - 1][1])
                    updateSnake(self)




class SearchBlock(object):
    def __init__(self, coord, parent=None, depth=0, cost=1):
        self.coord = coord
        self.i = coord[0]
        self.j = coord[1]
        self.parent = parent
        self.depth = depth
        self.cost = cost
        self.f = 0
        self.h = 0
        self.g = 0
        self.neighbors = []
        self.cols = 80
        self.row = 80
        self.obs = False
        self.dest = False

    def show(self, grid, color, st):
        # if self.closed is False:
        pygame.draw.rect(screen, color, (self.i * grid.width, self.j * grid.height, grid.width, grid.height), st)
        pygame.display.update()

    def addNeighbors(self, grid):
        i = self.i
        j = self.j
        if i < self.cols - 1 and grid[self.i + 1][j].obs is False:
            self.neighbors.append(grid[self.i + 1][j])
            if grid[self.i + 1][j].parent is None:
                grid[self.i + 1][j].cost = self.cost + 1
                grid[self.i + 1][j].parent = self
        if i > 0 and grid[self.i - 1][j].obs is False:
            self.neighbors.append(grid[self.i - 1][j])
            if grid[self.i - 1][j].parent is None:
                grid[self.i - 1][j].cost = self.cost + 1
                grid[self.i - 1][j].parent = self
        if j < self.row - 1 and grid[self.i][j + 1].obs is False:
            self.neighbors.append(grid[self.i][j + 1])
            if grid[self.i][j + 1].parent is None:
                grid[self.i][j + 1].cost = self.cost + 1
                grid[self.i][j + 1].parent = self
        if j > 0 and grid[self.i][j - 1].obs is False:
            self.neighbors.append(grid[self.i][j - 1])
            if grid[self.i][j - 1].parent is None:
                grid[self.i][j - 1].cost = self.cost + 1
                grid[self.i][j - 1].parent = self



# initial score
score = 0


# displaying Score function
def show_score(choice, color, font, size):
    # creating font object score_font
    score_font = pygame.font.SysFont(font, size)

    # create the display surface object
    # score_surface
    score_surface = score_font.render('Score : ' + str(score), True, color)

    # create a rectangular object for the
    # text surface object
    score_rect = score_surface.get_rect()

    # displaying text
    screen.blit(score_surface, score_rect)





def addApple(grid):
    t = random.randint(1, 79)
    w = random.randint(1, 79)
    appleDest = grid.grid[t][w]
    okSpawn = True
    if not appleDest.obs:
        for loc in range(0, len(snakeLocation)):
            if snakeLocation[loc][0] == t and snakeLocation[loc][1] == w:
                okSpawn = False
        if okSpawn:
            appleLocationX = t
            appleLocationY = w
            appleDest.show(grid, grid.apple, 0)
        else:
            addApple(grid)
    else:
        addApple(grid)


class PathFinder:
    path_cost = 0
    n_visit = 0
    nodesExpanded = 0
    notVisitedSet = set()
    nextToVisitSet = set()
    nextVisitCoord = set()
    notVisitedSet_conf = set()
    nextToVisitSet_conf = set()
    nextVisitCoord_conf = set()
    end = 0

    @staticmethod
    def heuristic(n, e):
        d = math.sqrt((n.i - e.i) ** 2 + (n.j - e.j) ** 2)
        # d = abs(n.i - e.i) + abs(n.j - e.j)
        return d



def clearOldSnakeLocation(grid):
    for location in range(0, len(snakeLocation)):
        grid.grid[snakeLocation[location][0]][snakeLocation[location][1]].show(grid, grid.grass, 0)


def updateSnake(grid):
    print(snakeLocation)
    for location in range(0, len(snakeLocation)):
        grid.grid[snakeLocation[location][0]][snakeLocation[location][1]].show(grid, (grid.snakeHead if location == 0 else grid.snakeBody), 0)


def gameLoop(grid):
    game_over = False
    while not game_over:
        print(appleLocationX)
        if snakeLocation[0][0] == appleLocationX and snakeLocation[0][1] == appleLocationY:
            addApple(grid)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    grid.moveLeft()
                elif event.key == pygame.K_RIGHT:
                    grid.moveRight()
                elif event.key == pygame.K_UP:
                    grid.moveUp()
                elif event.key == pygame.K_DOWN:
                    grid.moveDown()


def main():
    playGround = GridObj()
    playGround.createPlayGround()
    #show_score((0, 0, 0), 'Helvetica', 20)
    updateSnake(playGround)
    addApple(playGround)
    gameLoop(playGround)


if __name__ == "__main__":
    main()