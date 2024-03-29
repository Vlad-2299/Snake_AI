import math
import sys
import pygame
import queue
from sys import maxsize
import random
import time
import copy
import timeit

pygame.init()

running = True
window = True
############### WINDOW #######################################
screen = pygame.display.set_mode((400, 400))
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


snakeLocation = [(20, 20), (21, 20), (22, 20)]
lastSnakeNode = (0, 0)
# 1=left
# 2=right
# 3=up
# 4=down
global appleLocationX
global appleLocationY


class GridObj(object):
    def __init__(self):
        self.cols = 40
        self.grid = [0 for i in range(self.cols)]
        self.row = 40
        self.grass = (25, 255, 102)
        self.apple = (255, 255, 0)  # yellow
        self.snakeBody = (255, 0, 0)
        self.snakeHead = (179, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.grey = (220, 220, 220)
        self.width = 400 / self.cols
        self.height = 400 / self.row

    def createPlayGround(self):
        # create 2d array
        for i in range(self.cols):
            self.grid[i] = [0 for i in range(self.row)]

        # Create Spots
        for i in range(self.cols):
            for j in range(self.row):
                self.grid[i][j] = SearchBlock((i, j), None, 0, 1)
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

    def clearNodes(self):
        for i in range(1, self.cols - 1):
            for j in range(1, self.row - 1):
                self.grid[i][j] = SearchBlock((i, j), None, 0, 1)
                # self.grid[i][j].show(self, self.grass, 0)

    def moveSnake(self, move):
        #if ((snakeLocation[0][0]) - 1) != (snakeLocation[1][0]):
        if (snakeLocation[0][0] + move[0], snakeLocation[0][1] + move[1]) not in snakeLocation:
            tail = snakeLocation.pop()
            head = snakeLocation[0]
            snakeLocation.insert(0, (head[0] + move[0], head[1] + move[1]))
            for node in snakeLocation:
                self.grid[node[0]][node[1]].cost = maxsize
                self.grid[node[0]][node[1]].show(self, self.snakeBody, 0)
            self.grid[snakeLocation[0][0]][snakeLocation[0][1]].show(self, self.snakeHead, 0)
            self.grid[snakeLocation[1][0]][snakeLocation[1][1]].cost = 1
            if head[0] + move[0] == appleLocationX and head[1] + move[1] == appleLocationY:
                self.clearNodes()
                snakeLocation.append((tail[0], tail[1]))
                updateSnake(self)
                addApple(self)
            else:
                self.grid[tail[0]][tail[1]] = SearchBlock((tail[0], tail[1]), None, 0, 1)
                self.grid[tail[0]][tail[1]].show(self, self.grass, 0)
                self.grid[snakeLocation[0][0]][snakeLocation[0][1]].show(self, self.snakeHead, 0)
                self.grid[snakeLocation[1][0]][snakeLocation[1][1]].cost = 1
                self.grid[snakeLocation[1][0]][snakeLocation[1][1]].show(self, self.snakeBody, 0)
                self.grid[snakeLocation[1][0]][snakeLocation[1][1]].cost = maxsize
        else:
            print("Snake has eaten itself")


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
        # if i < self.cols - 1 and grid[self.i + 1][j].obs is False and (self.i + 1, j) != snakeLocation[1]:
        if i < self.cols - 1 and grid[self.i + 1][j].obs is False and (self.i + 1, j) not in snakeLocation:
            self.neighbors.append(grid[self.i + 1][j])
            if grid[self.i + 1][j].parent is None:
                grid[self.i + 1][j].cost = self.cost + 1
                grid[self.i + 1][j].parent = self
        # if i > 0 and grid[self.i - 1][j].obs is False and (self.i - 1, j) != snakeLocation[1]:
        if i > 0 and grid[self.i - 1][j].obs is False and (self.i - 1, j) not in snakeLocation:
            self.neighbors.append(grid[self.i - 1][j])
            if grid[self.i - 1][j].parent is None:
                grid[self.i - 1][j].cost = self.cost + 1
                grid[self.i - 1][j].parent = self
        # if j < self.row - 1 and grid[self.i][j + 1].obs is False and (self.i, j + 1) != snakeLocation[1]:
        if j < self.row - 1 and grid[self.i][j + 1].obs is False and (self.i, j + 1) not in snakeLocation:
            self.neighbors.append(grid[self.i][j + 1])
            if grid[self.i][j + 1].parent is None:
                grid[self.i][j + 1].cost = self.cost + 1
                grid[self.i][j + 1].parent = self
        #   if j > 0 and grid[self.i][j - 1].obs is False and (self.i, j - 1) != snakeLocation[1]:
        if j > 0 and grid[self.i][j - 1].obs is False and (self.i, j - 1) not in snakeLocation:
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
    t = random.randint(1, grid.cols - 1)
    w = random.randint(1, grid.row - 1)
    appleDest = grid.grid[t][w]
    okSpawn = True
    if not appleDest.obs:
        if (t, w) in snakeLocation:
            okSpawn = False
        if okSpawn:
            global appleLocationX
            appleLocationX = t
            global appleLocationY
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

    def A_star_search(cls, grid, ini_state, fin_state):
        frontier = queue.PriorityQueue()
        frontier.put(Prioritize(cls.heuristic(ini_state, fin_state), ini_state))
        explored = set()
        frontier_config_set = set()
        frontier_config_set.add(ini_state.coord)

        searchTime = time.process_time()

        while searchTime - time.process_time() < 0.1:
            state = frontier.get().item
            frontier_config_set.remove(state.coord)

            if state.coord == fin_state.coord:
                return state

            explored.add(state.coord)
            state.addNeighbors(grid.grid)
            neighbors = state.neighbors
            for iter in range(len(neighbors)):
                neighbor = neighbors[iter]
                if neighbor.coord not in explored:
                    if neighbor.coord not in frontier_config_set:
                        neighbor.g = state.g + state.cost
                        neighbor.f = neighbor.g + cls.heuristic(neighbor, fin_state)
                        frontier.put(Prioritize(neighbor.f, neighbor))
                        frontier_config_set.add(neighbor.coord)

        frontier.get().item

    @staticmethod
    def heuristic(n, e):
        d = math.sqrt((n.i - e.i) ** 2 + (n.j - e.j) ** 2)
        # d = abs(n.i - e.i) + abs(n.j - e.j)
        return d


def clearOldSnakeLocation(grid):
    for location in range(0, len(snakeLocation)):
        grid.grid[snakeLocation[location][0]][snakeLocation[location][1]].cost = 1
        grid.grid[snakeLocation[location][0]][snakeLocation[location][1]].show(grid, grid.grass, 0)


def updateSnake(grid):
    for node in snakeLocation:
        grid.grid[node[0]][node[1]].cost = maxsize
        grid.grid[node[0]][node[1]].show(grid, grid.snakeBody, 0)
    grid.grid[snakeLocation[0][0]][snakeLocation[0][1]].show(grid, grid.snakeHead, 0)
    grid.grid[snakeLocation[0][0]][snakeLocation[0][1]].cost = 1


def gameLoop(grid):
    game_over = False
    snakeDir = 0
    pathFinder = PathFinder()
    iniTime = time.process_time()
    while not game_over:  # create game mode options
        if appleLocationX != 0 and appleLocationY != 0 and snakeDir != 0:

            state = pathFinder.A_star_search(grid, grid.grid[snakeLocation[0][0]][snakeLocation[0][1]],
                                             grid.grid[appleLocationX][appleLocationY])
            finalState = state
            nextNode = (0, 0)
            while state.parent.coord != snakeLocation[0]:
                state = state.parent
                nextNode = state.coord
            if finalState.parent.coord == snakeLocation[0]:
                nextNode = state.coord

            move = (nextNode[0] - snakeLocation[0][0], nextNode[1] - snakeLocation[0][1])

            print(snakeLocation)
            print(str(nextNode) + ": Move cost: " + str(grid.grid[nextNode[0]][nextNode[1]].cost))
            if move == (0, -1):
                print("UP")
                snakeDir = 1
                grid.moveSnake(move)
            elif move == (0, 1):
                print("DOWN")
                snakeDir = 2
                grid.moveSnake(move)
            elif move == (-1, 0):
                print("LEFT")
                snakeDir = 3
                grid.moveSnake(move)
            elif move == (1, 0):
                print("RIGHT")
                snakeDir = 4
                grid.moveSnake(move)


        # if time.process_time() - iniTime >= 0.2:
        #     if snakeDir == 1:
        #         grid.moveLeft()
        #     elif snakeDir == 2:
        #         grid.moveRight()
        #     elif snakeDir == 3:
        #         grid.moveUp()
        #     elif snakeDir == 4:
        #         grid.moveDown()
        #     iniTime = time.process_time()

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if snakeDir != 1:
                        snakeDir = 3
                        grid.moveSnake((-1, 0))
                        iniTime = time.process_time()
                elif event.key == pygame.K_RIGHT:
                    if snakeDir != 2:
                        snakeDir = 4
                        grid.moveSnake((1, 0))
                        iniTime = time.process_time()
                elif event.key == pygame.K_UP:
                    if snakeDir != 3:
                        snakeDir = 1
                        grid.moveSnake((0, -1))
                        iniTime = time.process_time()
                elif event.key == pygame.K_DOWN:
                    if snakeDir != 4:
                        snakeDir = 2
                        grid.moveSnake((0, 1))
                        iniTime = time.process_time()


def main():
    playGround = GridObj()
    playGround.createPlayGround()
    # show_score((0, 0, 0), 'Helvetica', 20)
    updateSnake(playGround)
    addApple(playGround)
    gameLoop(playGround)


if __name__ == "__main__":
    main()
