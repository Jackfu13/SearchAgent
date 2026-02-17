import time
import numpy as np
from gridgame import *

##############################################################################################################################

# You can visualize what your code is doing by setting the GUI argument in the following line to true.
# The render_delay_sec argument allows you to slow down the animation, to be able to see each step more clearly.

# For your final submission, please set the GUI option to False.

# The gs argument controls the grid size. You should experiment with various sizes to ensure your code generalizes.
# Please do not modify or remove lines 18 and 19.

##############################################################################################################################

game = ShapePlacementGrid(GUI=True, render_delay_sec=0.5, gs=6, num_colored_boxes=5)
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
np.savetxt('initial_grid.txt', grid, fmt="%d")

##############################################################################################################################

# Initialization

# shapePos is the current position of the brush.

# currentShapeIndex is the index of the current brush type being placed (order specified in gridgame.py, and assignment instructions).

# currentColorIndex is the index of the current color being placed (order specified in gridgame.py, and assignment instructions).

# grid represents the current state of the board. 
    
    # -1 indicates an empty cell
    # 0 indicates a cell colored in the first color (indigo by default)
    # 1 indicates a cell colored in the second color (taupe by default)
    # 2 indicates a cell colored in the third color (veridian by default)
    # 3 indicates a cell colored in the fourth color (peach by default)

# placedShapes is a list of shapes that have currently been placed on the board.
    
    # Each shape is represented as a list containing three elements: a) the brush type (number between 0-8), 
    # b) the location of the shape (coordinates of top-left cell of the shape) and c) color of the shape (number between 0-3)

    # For instance [0, (0,0), 2] represents a shape spanning a single cell in the color 2=veridian, placed at the top left cell in the grid.

# done is a Boolean that represents whether coloring constraints are satisfied. Updated by the gridgames.py file.

##############################################################################################################################

shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

print(shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done)


####################################################
# Timing your code's execution for the leaderboard.
####################################################

start = time.time()  # <- do not modify this.



##########################################
# Write all your code in the area below.
##########################################
# Calculation for our objective function based on empty cells, violations, and shapes/colors used
#Used llm to help understand what our objective function should be based off
#check if a position is in bounds
def in_bounds(row,col):
    return (row >= 0  and row < game.gridSize) and (col >= 0  and col < game.gridSize)
def calc_score(grid, placedShapes):
    empty_count = 0
    violation_count = 0
    size = game.gridSize
    for i in range(size):
        for j in range(size):
            if grid[i][j] ==-1:
                empty_count +=1
            else:
                #only count right and below to avoid double counting if we count every neighbour
                if j < size - 1:
                    if grid[i][j] == grid[i][j+1]:
                        violation_count += 1
                if i < size - 1:
                    if grid[i][j] == grid[i+1][j]:
                        violation_count += 1
    num_shapes = len(placedShapes)
    colors_used = colors_used = len(set(grid[grid != -1]))
    return -(10*empty_count) - (30 * violation_count) - (num_shapes) - (2*colors_used)

#Finds a color that won't cause violations if we place this shape here. 
# Prefers color 0 or 1 to minimize total distinct colors used.
# Used LLm to debug code, originally the function was not finding a valid color, I didn't check if the new_pos was already
# in covered
def get_valid_color_for_shape(grid,shape,pos):
    covered = set()
    for i in range(len(shape)):
        for j in range(len(shape[0])):
            if shape[i][j] == 1:
                covered.add((pos[1] + i, pos[0] + j))
    cant_use = set()
    offset = [[-1,0],[0,1],[1,0],[0,-1]]
    for cover in covered:
        for x in offset:
            new_pos = (cover[0]+x[0],cover[1]+x[1])
            if new_pos not in covered and in_bounds(new_pos[0],new_pos[1]) and grid[new_pos[0],new_pos[1]] != -1:
                cant_use.add(grid[new_pos[0],new_pos[1]])

    valid = [c for c in range(0,4) if c not in cant_use]
    if not valid:
        return None
    preferred = [c for c in valid if c <= 1]
    if preferred: 
        return random.choice(preferred)
    return random.choice(valid)
#Given an empty cell, tries shapes from largest to smallest. 
# For each shape, checks every position where the shape would cover that cell. 
# Returns the first valid (shape, position, color) it finds.
def find_placement(grid, row, col):
    # Shuffle within size groups, but try big shapes first
    #Used LLM to help recommend using bigger shapes first, or else it would fill with 1 by 1.
    four_cell = [3, 4, 5, 6]
    three_cell = [7, 8]
    two_cell = [1, 2]
    one_cell = [0]

    random.shuffle(four_cell)
    random.shuffle(three_cell)
    random.shuffle(two_cell)

    shape_order = four_cell + three_cell + two_cell + one_cell

    for id in shape_order:
        shape = game.shapes[id]
        shape_h = len(shape)
        shape_w = len(shape[0])

        # Try every position where this shape would cover (row, col)
        for i in range(shape_h):
            for j in range(shape_w):
                if shape[i][j] == 1:
                 
                    pos_x = col - j
                    pos_y = row - i

                
                    if pos_x < 0 or pos_y < 0:
                        continue
                    if pos_x + shape_w > game.gridSize or pos_y + shape_h > game.gridSize:
                        continue

                    # Check if it can be placed
                    if game.canPlace(grid, shape, [pos_x, pos_y]):
                        color = get_valid_color_for_shape(grid, shape, [pos_x, pos_y])
                        if color is not None:
                            return (id, [pos_x, pos_y], color)

    return None
# Translates a planned move into execution. Moves brush, switches color and shapes, and then places
# Used LLm to debug, issue was not declaring global and forgetting to assign value when calling execute
def place_shape(shape_id, pos, color_id):
    global shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done
    
    while currentShapeIndex != shape_id:
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('switchshape')
    while shapePos[0] < pos[0]:
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('right')
    while shapePos[0] > pos[0]:
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('left')
    while shapePos[1] < pos[1]:
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('down')
    while shapePos[1] > pos[1]:
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('up')
    while currentColorIndex != color_id:
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('switchcolor')
    shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('place')

def restart():
    global shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done
    while placedShapes:
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('undo')

#Implement first choice hill climbing with random restarts
#Used LLM to help understand the flow of the hill climbing, such as picking random neighbours and random restarts
current_score = calc_score(grid, placedShapes)
stuck_count = 0

while not done:
    # Find all empty cells on the grid
    empty_cells = [(i, j) for i in range(game.gridSize) for j in range(game.gridSize) if grid[i][j] == -1]

    if not empty_cells:
        restart()
        current_score = calc_score(grid, placedShapes)
        stuck_count = 0
        continue

    row, col = random.choice(empty_cells)

    # Try to find a shape + color that covers this cell (biggest first)
    action = find_placement(grid, row, col)

    if action is None:
        stuck_count += 1
    else:
        shape_id, pos, color = action

        place_shape(shape_id, pos, color)

        # Check if the score improved
        new_score = calc_score(grid, placedShapes)
        if new_score >= current_score:
            current_score = new_score
            stuck_count = 0
        else:
            shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('undo')
            stuck_count += 1

    # If stuck for too long, random restart, undo everything and try again
    if stuck_count > 300:
        restart()
        current_score = calc_score(grid, placedShapes)
        stuck_count = 0




########################################

# Do not modify any of the code below. 

########################################

end=time.time()

np.savetxt('grid.txt', grid, fmt="%d")
with open("shapes.txt", "w") as outfile:
    outfile.write(str(placedShapes))
with open("time.txt", "w") as outfile:
    outfile.write(str(end-start))
