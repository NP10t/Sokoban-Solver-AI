import os
import psutil
from copy import deepcopy
from time import time
from collections import deque
import heapq # min-heap by default


class State:
    def __init__(self, Ares=None, stones=None):
        self.Ares = Ares
        self.stones = stones if stones is not None else [] # A stone info includes x, y, its weight

class Item:
    def __init__(self, state=None, path=None):
        self.state = state if state is not None else State()
        self.path = path if path is not None else []

    def __lt__(self, other):
        return True

class Solver:
    def __init__(self, inputFile):
        self.firstState = State() # The first state of the matrix
        self.switches = [] # Coodinates of switches
        self.firstBoard = [] # The first matrix only includes walls, switches, and positions that stones can't be placed on
        self.actions = {"u": (-1,0), "U": (-1,0), "l": (0,-1), "L": (0,-1), "d": (1,0), "D": (1,0), "r": (0,1), "R":(0,1)}
        self.nStones = 0 # Number of stones

        # Parse input
        with open(inputFile, 'r') as file:
            self.lines = file.readlines()

        self.nRows = 0 # Number of rows
        self.nCols = 0 # Number of columns

        # The list to store where walls start and end on this row    
        self.wallRows = [] 
        # The list to store where walls start and end on this column
        self.wallCols = []

        # The bool array to keep track if this row has switch
        self.rowSwitch = []
        # The bool array to keep track if this column has switch
        self.colSwitch = []

        # The bool array to keep track if this row is full of walls
        self.rowFullWalls = []
        # The bool array to keep track if this column if full of walls
        self.colFullWalls = []

        countLines = 0
        for line in self.lines:
            currentLine = line.strip('\n')
            if countLines == 0:
                self.wArr = [int(weight) for weight in currentLine.split()]
            else: 
                row = []
                # Where walls start
                wallStart = -1

                # Where walls end
                wallEnd = -1

                # Flag: if this row has switch
                flag = False

                # Signal: if this row is full of walls
                signal = True

                if len(currentLine) > self.nCols: # Number of columns
                    self.nCols = len(currentLine)

                for c in range(len(currentLine)):
                    if currentLine[c] == '#':
                        row.append('#')

                        if wallStart == -1: # If walls start from here on this row
                            wallStart = c

                        wallEnd = c # Update wallEnd so that it keeps where walls end on this row   

                    elif currentLine[c] == '+' or currentLine[c] == '.':
                        # This row has switch
                        flag = True
                        # This row is not full of walls
                        signal = False

                        row.append('.')
                    elif currentLine[c] == '*':
                        flag = True
                        signal = False
                        row.append('*')
                    else:
                        if currentLine[c] == '@' or currentLine[c] == '$':
                            # This row is not full of walls
                            signal = False
                        row.append(' ')

                    self.adder(currentLine[c], countLines-1, c) 

                # Store whether this row has switch
                self.rowSwitch.append(flag)

                # Store where walls start and end on this row
                self.wallRows.append((wallStart, wallEnd)) 

                # Store whether this row is full of walls
                self.rowFullWalls.append(signal)

                # Append the row
                self.firstBoard.append(row)    
            countLines += 1

        # Number of columns
        self.nRows = countLines - 1


        print("\n")    

        # Rescrutinize each row whether it is full of walls
        for i in range(self.nRows):
            if self.rowFullWalls[i] == True:
                (wallStart, wallEnd) = self.wallRows[i]
                # signal to check
                signal = True
                for j in range(wallStart,wallEnd):
                    if self.firstBoard[i][j] != '#': # If this is not wall
                        signal = False
                        break
                self.rowFullWalls[i] = signal    

        # Find where walls start and end on columns (of self.firstBoard)
        # Mark column if it has switch on it
        # Mark column if it is full of walls
        for i in range(self.nCols):
            # Where walls start
            wallStart = -1

            # Where walls end
            wallEnd = -1

            # Whether this column has switch
            flag = False

            # Whether this column is full of walls
            signal = True

            for j in range(self.nRows):
                if i >= len(self.firstBoard[j]):
                    continue
                if self.firstBoard[j][i] == '#':
                    if wallStart == -1:
                        wallStart = j # Update wallStart only once
                    wallEnd = j # Update wallEnd
                elif self.firstBoard[j][i] == '.' or self.firstBoard[j][i] == '*' or self.firstBoard[j][i] == '+':
                    flag = True # This column has switch
                    signal = False
                elif self.firstBoard[j][i] == '@' or self.firstBoard[j][i] == '$':
                    signal = False
            self.colSwitch.append(flag)
            self.wallCols.append((wallStart, wallEnd))
            self.colFullWalls.append(signal)

        # Rescrutinize to check each column whether it is full of columns
        for i in range(self.nCols):
            if self.colFullWalls[i] == True:
                (wallStart, wallEnd) = self.wallCols[i]
                signal = True
                for j in range(wallStart, wallEnd):
                    if self.firstBoard[j][i] != '#':
                        signal = False
                        break
                self.colFullWalls[i] = signal    

        self.markPlaces()        

    def markPlaces(self):
        # If row x is full of walls, check row x-1 and row x+1 
        # If row x-1 does not have switch, mark postitions of row x-1 so that stones cannnot be placed on free spaces
        # ... x + 1
        for i in range(self.nRows):
            # If this row is full of walls
            if self.rowFullWalls[i]:
                if (i > 0 and self.rowSwitch[i-1] == False): # Row i - 1 does not have switch
                    for j in range(self.nCols):
                        if j < self.wallRows[i][1] and \
                                i-1 < self.wallCols[j][1] and \
                                self.firstBoard[i-1][j] != '#': # If this position is not wall, it must be whitespace
                                    self.firstBoard[i-1][j] = '!' # Stones cannot be placed on this position

                if (i < self.nRows - 1 and self.rowSwitch[i+1] == False): # Row i + 1 does not have switch 
                    for j in range(self.nCols):
                        if j < self.wallRows[i+1][1] and \
                                i+1 < self.wallCols[j][1] and \
                                self.firstBoard[i+1][j] != '#':
                                    self.firstBoard[i+1][j] = '!'

        # The same strategy applies to columns
        for i in range(self.nCols):
            # If this column is full of walls
            if self.colFullWalls[i]:
                if (i > 0  and self.colSwitch[i-1] == False): # Column i - 1 does not have switch
                    for j in range(self.nRows):
                        if j < self.wallCols[i][1] and \
                                i-1 < self.wallRows[j][1] and \
                                self.firstBoard[j][i-1] != '#':
                                    self.firstBoard[j][i-1] = '!'
                if (i < self.nCols -1 and self.colSwitch[i+1] == False): # Column i + 1 does not have switch
                    for j in range(self.nRows):
                        if j < self.wallCols[i+1][1] and \
                                i+1 < self.wallRows[j][1] and\
                                self.firstBoard[j][i+1] != '#':
                                    self.firstBoard[j][i+1] = '!'

    def adder(self, char, x, y): # x: top to bottom, y: left to right
        if char == '@':
            self.firstState.Ares = [x,y]
        elif char == '+':
            self.firstState.Ares = [x,y]
            self.switches.append((x,y))
        elif char == '$':
            self.firstState.stones.append([x,y,self.wArr[self.nStones]])
            self.nStones += 1
        elif char == '.':
            self.switches.append([x,y])
        elif char == '*':
            self.firstState.stones.append([x,y,self.wArr[self.nStones]])
            self.nStones += 1
            self.switches.append([x,y])


    def generateChild(self, currentState, path, action): # currentState, path, action are deepcopy versions
        x = currentState.Ares[0] + self.actions[action][0]
        y = currentState.Ares[1] + self.actions[action][1]

        # The cost of action
        weight = 0
        # print(currentState.Ares," ", action)
        if self.firstBoard[x][y] == '#':
            # print("alo")
            return False

        if action.islower():
            for stone in currentState.stones:
                if x == stone[0] and y == stone[1]:
                    return False

        if action.isupper():
            # Index of stone
            idx = -1

            # Check if Ares will really push a stone
            for i in range(self.nStones):
                stone = currentState.stones[i]
                if stone[0] == x and stone[1] == y:
                    idx = i
                    weight = stone[2]
                    break

            # if there are no stones in (x,y)
            if idx == -1:
                # print("idx: ", action)
                return False

            # If stone is alrady on switch, return False
            #if self.firstBoard[x][y] == '.' or self.firstBoard[x][y] == '*':
                #return False

            # The new coordinates of this stone
            x += self.actions[action][0]
            y += self.actions[action][1] 

            # If the new postion of stone is already placed by another stone
            for stone in currentState.stones:
                if stone[0] == x and stone[1] == y:
                    return False

            # Check "Deadlock" - The position to push to is not placeable
            if self.firstBoard[x][y] == '!':
                return False

            # The positon to push to is wall
            if self.firstBoard[x][y] == '#':
                return False

            # All check passed, update the coordinates of the pushed stone
            currentState.stones[idx][0] = x
            currentState.stones[idx][1] = y

        # Update coordinates of Ares
        currentState.Ares[0] += self.actions[action][0]
        currentState.Ares[1] += self.actions[action][1]

        # Update Path
        path.append([action,weight])

        # print("In generate: ", currentState.Ares)

        return Item(currentState, path)


    def display(self):
        print("\nAres: ", self.firstState.Ares)
        print("Weights of stones: ", end="")
        for w in self.wArr:
            print(str(w) + " ", end="")
        print("\nStones coordinates: ")    
        for stone in self.firstState.stones:
            print(stone)
        print("\n")    
        for row in self.firstBoard:
            print(row)   
        print("\nCoordinates of switches:")
        for switch in self.switches:
            print(switch)
        print("\n")  
        for action in self.actions.keys():
            if action.islower():
                print("low")
            else:
                print("up")

    def makeBoard(self, currentState): # This function makes a board based on the currentState
        board = deepcopy(self.firstBoard)
        Ares = currentState.Ares
        if board[Ares[0]][Ares[1]] == '.': # Ares stands on switch
            board[Ares[0]][Ares[1]] = '+'
        else:
            board[Ares[0]][Ares[1]] = '@'

        for stone in currentState.stones:
            if board[stone[0]][stone[1]] == '.' or board[stone[0]][stone[1]] == '*':
                board[stone[0]][stone[1]] = '*'
            else:
                board[stone[0]][stone[1]] = '$'
        return board        

    def isGoalState(self, currentState):
        for stone in currentState.stones:
            x = stone[0]
            y = stone[1]
            if self.firstBoard[x][y] != '.' and self.firstBoard[x][y] != '*':
                return False
        return True    

    def isStone(self, x, y, board):
        if board[x][y] == '$' or board[x][y] == '*':
            return True
        return False

    def checkBlockedByStones(self, currentState, board): 
        """
        $$
        $$
        """
        for stone in currentState.stones:
            x = stone[0]
            y = stone[1]
            if board[x][y] == '.' or board[x][y] == '*':
                continue
            # print("x = ", x, " y = ", y)
            """
            s$
            $$
            """
            if y+1 < self.wallRows[x+1][1] and \
                    self.isStone(x,y+1,board) and self.isStone(x+1,y,board) and self.isStone(x+1,y+1,board):
                        return True
            """
            $$
            s$
            """
            if y+1 < self.wallRows[x-1][1] and \
                    self.isStone(x,y+1,board) and self.isStone(x-1,y,board) and self.isStone(x-1,y+1,board):
                        return True
            """
            $$
            $s
            """
            if self.isStone(x-1,y-1,board) and self.isStone(x,y-1,board) and self.isStone(x-1,y,board):
                return True
            """
            $s
            $$
            """
            if self.isStone(x,y-1,board) and self.isStone(x+1,y-1,board) and self.isStone(x+1,y,board):
                return True
        return False       

    def checkRoundCornered(self, currentState, board): # There is a stone that's cannot be moved
        for stone in currentState.stones:
            x = stone[0]
            y = stone[1]
            if (board[x][y] == '.' or board[x][y] == '*'):
                continue
            if (board[x-1][y] == '#' and board[x][y-1] == '#'):
                """ 
                     #   
                    #s
                """
                return True
            if (board[x-1][y] == '#' and board[x][y+1] == '#'):
                """
                    #
                    s#
                """
                return True
            if (board[x][y-1] == '#' and board[x+1][y] == '#'):
                """
                    #s
                     #
                """
                return True
            if (board[x][y+1] == '#' and board[x+1][y] == '#'):
                """
                    s#
                    #
                """
                return True
        return False    

    def checkDeadLock(self, currentState):
        copiedState = deepcopy(currentState)
        board = self.makeBoard(copiedState)

        if self.checkBlockedByStones(copiedState, board):
            return True
        if self.checkRoundCornered(copiedState, board):
            return True
        for stone in copiedState.stones:
            x = stone[0]
            y = stone[1]
            if self.firstBoard[x][y] == '!':
                return True

        return False   

    def calculateCost(self, path):
        totalWeight = 0
        for action in path:
            totalWeight += action[1]
        return totalWeight    

    def writeOutput(self, flag, alg, steps, nodes, path, time, memory, fileNumber):
    	# Open output file
    	with open(f"output-{fileNumber}.txt", "a") as file:
            # Name of alg
            file.write(f"{alg}\n")

            # Check wherther soltuion exists
            if not flag:
                file.write("There are no solutions\n")
                file.write(f"Steps: 0, Weight: 0, Node: {nodes}, Time (ms): {time * 1000:.2f}, Memory (MB): {memory / (1024 ** 2):.2f}\n")
                return

            # Calculate weight
            totalWeight = self.calculateCost(path) if steps != 0 else 0
            file.write(f"Steps: {steps}, Weight: {totalWeight}, Node: {nodes}, Time (ms): {time * 1000:.2f}, Memory (MB): {memory / (1024 ** 2):.2f}\n")

            # Path
            path_str = "".join(action[0] for action in path)
            file.write(f"{path_str}\n")

    def manhattanDistance(self, stone, switch):
        return abs(switch[0] - stone[0]) + abs(switch[1] - stone[1])


    def calculateHeuristic(self, currentState):
        hVal = 0
        for i in range(len(currentState.stones)):
            stone = currentState.stones[i]
            hmin = min(self.manhattanDistance(stone, switch) * stone[2] for switch in self.switches)
            hVal += hmin
        return hVal

    def isVisited(self, currentState, visitedStates):
        for state in visitedStates:
            if state.Ares == currentState.Ares and state.stones == currentState.stones:
                return True
        return False    


    def AStar(self, fileNumber):       
        start = time()
        nodes = 0

        # Get the current info of RAM
        process = psutil.Process()
        mem_before = process.memory_info().rss

        # Path
        path = []

        # Initialize queue
        frontier = []

        # First item includes firstState and empty path 
        item = Item(self.firstState, path)

        # Calculate the priority of firstState
        hVal = self.calculateHeuristic(self.firstState)

        # Push the item
        heapq.heappush(frontier, (hVal, item))

        # Visited items
        visitedStates = []

        while True:
            if len(frontier) == 0:
                # Stop timer
                end = time()
                # Get the current info of RAM
                mem_after = process.memory_info().rss
                # write Output
                self.writeOutput(False, "A*", 0, nodes, "", end-start, mem_after - mem_before, fileNumber)
                return 0

            priority, item = heapq.heappop(frontier)
            nodes += 1
            currentState = item.state
            path = item.path

            # Check goal state first    
            if self.isGoalState(currentState):
                # Stop timer
                end = time()
                # Get the current info of RAM
                mem_after = process.memory_info().rss
                # Write Output
                self.writeOutput(True, "A*", len(path), nodes, path, end-start, mem_after - mem_before, fileNumber)
                return path

            # Mark visited
            visitedStates.append(currentState)

            # Check deadlock cannot validate whether this state is the goal state
            if self.checkDeadLock(currentState):
                continue

            for move in self.actions.keys():
                copiedState = deepcopy(currentState)
                copiedPath = deepcopy(path)
                action = deepcopy(move)
                child = self.generateChild(copiedState, copiedPath, action)

                # Check if the child is valid
                if child == False:
                    continue

                if self.isVisited(child.state, visitedStates) == False:
                    hVal = self.calculateHeuristic(child.state)
                    cost = self.calculateCost(child.path)
                    heapq.heappush(frontier, (hVal + cost, child))


    def Ucs(self, fileNumber):       
        # Start timer
        start = time()
        nodes = 0
        
        # Get the current info of RAM
        process = psutil.Process()
        mem_before = process.memory_info().rss

        # Path
        path = []

        # Initialize queue
        frontier = []

        # First item includes firstState and empty path 
        item = Item(self.firstState, path)

        # Push the item
        heapq.heappush(frontier, (0, item))

        # Visited items
        visitedStates = []

        while True:
            if len(frontier) == 0:
                # Stop timer
                end = time()
                # Get the current info of RAM
                mem_after = process.memory_info().rss
                # write Output
                self.writeOutput(False, "UCS", 0, nodes, "", end-start, mem_after - mem_before, fileNumber)
                return 0

            priority, item = heapq.heappop(frontier)
            nodes += 1
            currentState = item.state
            path = item.path

            # Check goal state first
            if self.isGoalState(currentState):
                # Stop timer
                end = time()
                # Get the current info of RAM
                mem_after = process.memory_info().rss
                # Write output
                self.writeOutput(True, "UCS", len(path), nodes, path, end-start, mem_after - mem_before, fileNumber)
                return path
            
            # Mark visited
            visitedStates.append(currentState)

            # Check deadlock cannot validate whether this state is the goal state
            if self.checkDeadLock(currentState):
                continue

            for move in self.actions.keys():
                copiedState = deepcopy(currentState)
                copiedPath = deepcopy(path)
                action = deepcopy(move)
                child = self.generateChild(copiedState, copiedPath, action)

                # Check if the child is valid
                if child == False:
                    continue

                if self.isVisited(child.state, visitedStates) == False:
                    cost = self.calculateCost(child.path)
                    heapq.heappush(frontier, (cost, child))


    def Bfs(self, fileNumber):
        # Start timer
        start = time()
        nodes = 0
        
        # Get the current info of RAM
        process = psutil.Process()
        mem_before = process.memory_info().rss
        
        # Path
        path = []
        
        # Initialize queue
        self.queue = deque()
        
        # First item includes firstState and empty path
        item = Item(self.firstState, path)

        # Push the first item
        self.queue.append(item)
        
        # Visited items
        visitedStates = []

        # Mark visited fisrtState
        visitedStates.append(self.firstState)

        while True:
            if len(self.queue) == 0:
                # Stop timer
                end = time()
                # Get ther current info of RAM
                mem_after = process.memory_info().rss
                # Write output
                self.writeOutput(False, "BFS", 0, nodes, "", end-start, mem_after - mem_before, fileNumber)
                return False

            item = self.queue.popleft()
            nodes += 1
            currentState = item.state
            path = item.path

            # Check goal state
            if self.isGoalState(currentState):
                # Stop timer
                end = time()
                # Get the current info of RAM
                mem_after = process.memory_info().rss
                # Write output
                self.writeOutput(True, "BFS", len(path), nodes, path, end-start, mem_after - mem_before, fileNumber)
                return path

            # Check Deadlock
            if self.checkDeadLock(currentState):
                continue

            for move in self.actions.keys():
                copiedState = deepcopy(currentState)
                copiedPath = deepcopy(path)
                action = deepcopy(move)
                child = self.generateChild(copiedState,copiedPath, action)

                # Check if the child is valid
                if child == False:
                    continue

                if self.isVisited(child.state,visitedStates) == False:
                    visitedStates.append(child.state)
                    self.queue.append(child)

    def Dfs(self, fileNumber):
        # Start timer
        start = time()
        nodes = 0
        
        # Get the current info of RAM
        process = psutil.Process()
        mem_before = process.memory_info().rss
        
        # Path
        path = []

        # Initilize stack
        self.stack = []

        # First item includes firstState and empty path
        item = Item(self.firstState, path)
        
        # Push the first item
        self.stack.append(item)

        # Visited items
        visitedStates = []

        # Mark the firstState
        visitedStates.append(self.firstState)

        while True:
            if len(self.stack) == 0:
                # Stop timer
                end = time()
                # Get the current info of RAM
                mem_after = process.memory_info().rss
                # Write output
                self.writeOutput(False, "DFS", 0, nodes, "", end-start, mem_after - mem_before, fileNumber)
                return False
            
            item = self.stack.pop()
            nodes += 1
            currentState = item.state
            path = item.path

            # Check goal state
            if self.isGoalState(currentState):
                # Stop timer
                end = time()
                # Get the current info of RAM
                mem_after = process.memory_info().rss
                # Write output
                self.writeOutput(True, "DFS", len(path), nodes, path, end-start, mem_after - mem_before, fileNumber)
                return path

            # Check deadlock
            if self.checkDeadLock(currentState):
                continue

            for move in self.actions.keys():
                copiedState = deepcopy(currentState)
                copiedPath = deepcopy(path)
                action  = deepcopy(move)
                child = self.generateChild(copiedState,copiedPath,action)

                # Check if the child is valid
                if child == False:
                    continue

                if self.isVisited(child.state,visitedStates) == False:
                    visitedStates.append(child.state)
                    self.stack.append(child)




def solve_with_strategy(file, algo):
    # print("tao la yua")
    # file = "01"
    inputFile = os.path.join(os.getcwd(), 'input-'+file+'.txt')
    sokobanBoard = Solver(inputFile)
    
    
    data = []
    print(algo)
    if algo == "bfs":
        data = sokobanBoard.Bfs(file)
    elif algo == "dfs":
        data = sokobanBoard.Dfs(file)
    elif algo == "ucs":
        data = sokobanBoard.Ucs(file)
    elif algo == "a*":
        data = sokobanBoard.AStar(file)
    
    path = ''.join(item[0] for item in data)
    weights = [item[1] for item in data]
    
    return path, weights

# a, _ = solve_with_strategy("01", "dfs")
# print("x")
# print(a)