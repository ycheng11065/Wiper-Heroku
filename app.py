# Welcome to
# __________         __    __  .__                               __https://Wiper.abhijoymandal.repl.co
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import random
import typing

#Ranking:
# 1: Larger Snake
# 2: Space
# 3: Food
# 4: Kills

MIN_SCORE = float('-inf')
DEFAULT_SCORE = 0
LARGER_SNAKE_DANGER = 3
SAME_SNAKE_DANGER = 1
SMALLER_SNAKE_REWARD = 0.5
EDGE_KILL_WEIGHT = 2

HP_THRESH = 30
LENGTH_AIM = 2
len_you = 0

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#3399FF",  # TODO: Choose color
        "head": "do-sammy",  # TODO: Choose head
        "tail": "do-sammy",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
# float('-inf')  Replace false
# any number not negative infinity replace true
  
    is_move_safe = {
      "up": DEFAULT_SCORE, 
      "down": DEFAULT_SCORE, 
      "left": DEFAULT_SCORE, 
      "right": DEFAULT_SCORE
    }

    # The essential variables
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
    my_body = game_state['you']['body'] 
    my_opp = game_state['board']['snakes']
    food = game_state["board"]["food"]
    len_you = game_state['you']["length"]
    game_Width = game_state["board"]["width"]
    game_Height = game_state["board"]["height"]
    print(len_you)

    map = [[0 for i in range(game_Width)] for j in range(game_Height)]
    length_map = [[0 for i in range(game_Width)] for j in range(game_Height)]
    map, length_map = setBound(map, length_map, my_opp, game_state)
    # We've included code to prevent your Battlesnake from moving backwards
    is_move_safe = prevent_back(game_state, is_move_safe, my_head, my_neck)
    # TODO: Step 1 - Prevent your Battlesnake from moving out of bounds
    is_move_safe = out_of_bounds(game_state, is_move_safe, my_head)
    # TODO: Step 2 - Prevent your Battlesnake from colliding with itself
    is_move_safe = self_collision(is_move_safe, my_head, my_body)
    # TODO: Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
    is_move_safe = opp_collision(game_state, is_move_safe, my_head, my_body, my_opp)
    #print(f'scores: {is_move_safe}')
        
    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe>MIN_SCORE:
            safe_moves.append(move)

    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}
    # TODO: Step 4 - Move towards food instead of random, to regain health and survive longer
    # food = game_state['board']['food']
    spaces = floodFill(map, game_Width, game_Height, my_head["x"], my_head["y"])
    print(f'spaces: {spaces}')
    # Future improvement one loop
    max_space = max([space for _, space in spaces.items() ])
    largest = [move for move, space in spaces.items() if space==max_space]
    for move in largest:
      is_move_safe[move]+=1
    if should_find_food(game_state, my_opp):
      is_move_safe = find_food(game_state, is_move_safe, my_head, food, length_map)
      print("find food")
    is_move_safe = can_edge_kill(game_state, is_move_safe)
    is_move_safe = score(game_state, my_head, is_move_safe, map)
    print(f'scores: {is_move_safe}')
    bestScore = max([score for _, score in is_move_safe.items()])   #excess runtime?
    best_moves = [move for move, score in is_move_safe.items() if score==bestScore]
    # Choose a random move from the safe ones
    #next_move = random.choice(best_moves)
    next_move = best_moves[0]
    if best_moves == ["left", "right"] or best_moves == ["rigth", "left"]:
      if my_head["x"]<game_Width//2:
        next_move = "right"
      else:
        next_move = "left" 
    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}

# Start server when `python main.py` is run
def out_of_bounds(game_state, moves, head):
  board_width = game_state['board']['width']
  board_height = game_state['board']['height']
  if head["x"]>=board_width-1:
    moves["right"] = MIN_SCORE
  if head["x"]<=0:
    moves["left"] = MIN_SCORE
  if head["y"]<=0:
    moves["down"] = MIN_SCORE
  if head["y"]>=board_height-1:
    moves["up"] = MIN_SCORE
  return moves

def prevent_back(game_state, moves, head, neck):
    if neck["x"] < head["x"]:  # Neck is left of head, don't move left
      moves["left"] = MIN_SCORE

    elif neck["x"] > head["x"]:  # Neck is right of head, don't move right
      moves["right"] = MIN_SCORE

    elif neck["y"] < head["y"]:  # Neck is below head, don't move down
      moves["down"] = MIN_SCORE

    elif neck["y"] > head["y"]:  # Neck is above head, don't move up
      moves["up"] = MIN_SCORE
    return moves

def self_collision(moves, head, body):
  for i in range(len(body)): 
      assign_score = MIN_SCORE
      if (i == 0 or i == 1):  # Skip Head and Neck
        continue;
        
      curr_x = body[i]["x"];  # Current body's x value
      curr_y = body[i]["y"];  # Current body's y value
      if  i==len(body)-1:
        assign_score = -0.5
      if head["y"] == curr_y: 
        if head["x"] + 1 != None and head["x"] + 1 == curr_x:
          moves["right"] += assign_score
        elif head["x"] - 1 != None and head["x"] - 1 == curr_x:
          moves["left"] += assign_score
      elif head["x"] == curr_x:
         if head["y"] + 1 != None and head["y"] + 1 == curr_y:
          moves["up"] += assign_score
         elif head["y"] - 1 != None and head["y"] - 1 == curr_y:
          moves["down"] += assign_score
  return moves

# Delete excess checks after map is implemented
def opp_collision(game_state, moves, head, body, opp):
  for i in range(len(opp)):
      if game_state["you"]["id"] == opp[i]["id"]:
        continue
      for j in range(len(opp[i]["body"])):
        curr_body = opp[i]["body"][j]
        if (head["x"] == curr_body["x"]):
          if (head["y"] + 1 != None and head["y"] + 1 == curr_body["y"]):
            moves["up"] += MIN_SCORE;
          elif (head["y"] - 1 != None and head["y"] - 1 == curr_body["y"]):
            moves["down"] += MIN_SCORE;

        elif (head["y"] == curr_body["y"]):
          if (head["x"] + 1 != None and head["x"] + 1 == curr_body["x"]):
            moves["right"] += MIN_SCORE;
          elif (head["x"] - 1 != None and head["x"] - 1 == curr_body["x"]):
            moves["left"] += MIN_SCORE;
            
  return moves
  

def dist(a, b):
  return abs(a["x"]-b["x"])+abs(a["y"]-b["y"])

def should_find_food(game_state, opp):
  snakes = game_state["board"]["snakes"][:]
  me = game_state["you"]
  snakes.remove(me)
  
  if me["health"] < HP_THRESH:
    return True
  if len(snakes)==0:
    return False
   
  lengths = [snake["length"] for snake in snakes]
 # if (len(opp) > 1):   #Only active when more than 1 snake on field
  if me["length"] - max(lengths) <= LENGTH_AIM:
      return True  
  return False


def find_food(game_state, moves, head, foods, length_map):
  closest = float("inf")
  min_food = {}
  FOOD_WEIGHT = HP_THRESH/game_state["you"]["health"]
  for food in foods:
    distance = dist(head, food)
    if distance<closest:
      min_food=food
      closest = distance
  if min_food == {}:
    return moves
  
  if min_food["x"]>head["x"]:
    moves["right"]+=FOOD_WEIGHT
  if min_food["x"]<head["x"]:
    moves["left"]+=FOOD_WEIGHT
  if min_food["y"]>head["y"]:
    moves["up"]+=FOOD_WEIGHT
  if min_food["y"]<head["y"]:
    moves["down"]+=FOOD_WEIGHT
  return moves



# def food_inspection(game_state, moves, head, food, length_map):
#   is_safe = True
#   my_length = game_state["you"]["length"]
#   if food["x"]>head["x"]:
#     is_safe = is_safe and length_map[head["x"]+1][head["y"]]<my_length and length_map[head["x"]+2][head["y"]]<my_length
#   if food["x"]<head["x"]:
#     moves["left"]+=FOOD_WEIGHT
#   if food["y"]>head["y"]:
#     moves["up"]+=FOOD_WEIGHT
#   if food["y"]<head["y"]:
#     moves["down"]+=FOOD_WEIGHT

# def check_bound(head, food):
#   h_x = head["x"]
#   h_y = head["y"]
#   f_x = food["x"]
#   f_y = food["y"]
#   dir = (h_x-f_x, h_y-f_y)
  
  


def can_edge_kill(game_state, moves):
  snakes = game_state["board"]["snakes"]
  my_id = game_state["you"]["id"]
  me = game_state["you"]["body"][0]
  my_neck = game_state["you"]["body"][1]
  my_dir = (me["x"]-my_neck["x"], me["y"]-my_neck["y"])
  board_height = game_state["board"]["height"]
  board_width = game_state["board"]["width"]
  if len(snakes)==2:
    other_s = snakes[0] if snakes[0]["id"]!=my_id else snakes[1]
    other = other_s["body"][0]
    other_neck = other_s["body"][1]
    other_dir = (other["x"]-other_neck["x"], other["y"]-other_neck["y"])

    #when trapped other in bottom of the board
    if (me["y"]==1 and other["y"]==0) and (me["x"]>other["x"]):
      moves["right"]+=EDGE_KILL_WEIGHT
    elif (me["y"]==1 and other["y"]==0) and (me["x"]<other["x"]):
      moves["left"]+=EDGE_KILL_WEIGHT
    elif (me["y"]==1 and other["y"]==0) and (me["x"]==other["x"]) and other_dir==my_dir:
      moves["left"]+=EDGE_KILL_WEIGHT
      moves["right"]+=EDGE_KILL_WEIGHT

    #when trapped other at left edge of the board
    elif (me["x"]==1 and other["x"]==0) and (me["y"]>other["y"]):
      moves["up"]+=EDGE_KILL_WEIGHT
    elif (me["x"]==1 and other["x"]==0) and (me["y"]<other["y"]):
      moves["down"]+=EDGE_KILL_WEIGHT
    elif (me["x"]==1 and other["x"]==0) and (me["y"]==other["y"]) and other_dir==my_dir:
      moves["down"]+=EDGE_KILL_WEIGHT
      moves["up"]+=EDGE_KILL_WEIGHT

    #when trapped other at the top of the board
    elif (me["y"]==board_height-2 and other["y"]==board_height-1) and (me["x"]>other["x"]):
      moves["right"]+=EDGE_KILL_WEIGHT
    elif (me["y"]==board_height-2 and other["y"]==board_height-1) and (me["x"]<other["x"]):
      moves["left"]+=EDGE_KILL_WEIGHT
    elif (me["y"]==board_height-2 and other["y"]==board_height-1) and (me["x"]==other["x"]) and other_dir==my_dir:
      moves["left"]+=EDGE_KILL_WEIGHT
      moves["right"]+=EDGE_KILL_WEIGHT

      #when trapped other at the right edge of the board
    elif (me["x"]==board_width-2 and other["x"]==board_width-1) and (me["y"]<other["y"]):
      moves["up"]+=EDGE_KILL_WEIGHT
    elif (me["x"]==board_width-2 and other["x"]==board_width-1) and (me["y"]>other["y"]):
      moves["down"]+=EDGE_KILL_WEIGHT
    elif (me["x"]==board_width-2 and other["x"]==board_width-1) and (me["y"]==other["y"]) and other_dir==my_dir:
      moves["down"]+=EDGE_KILL_WEIGHT
      moves["up"]+=EDGE_KILL_WEIGHT
      
  return moves

# Return array with number of space to every possible move
def floodFill(map, width, height, x, y):
  dir = [[0, 1], [0, -1], [-1, 0], [1, 0]]
  space = {"up":0, "down":0, "right":0, "left":0}
  for d in dir:
    curr_x = x + d[0]
    curr_y = y + d[1]
    if (curr_x < 0 or curr_y < 0 or curr_x >= width or curr_y >= height): continue
    col_map = [row[:] for row in map]  # New copy
    if (map[curr_x][curr_y] == 1):
      continue
    if d == [1, 0]:
      space["right"] = fill(col_map, width, height, curr_x, curr_y)
    elif d == [-1, 0]:
      space["left"] = fill(col_map, width, height, curr_x, curr_y)
    elif d == [0, 1]:
      space["up"] = fill(col_map, width, height, curr_x, curr_y)
    else:
      space["down"] = fill(col_map, width, height, curr_x, curr_y)
  return space

def fill(map, width, height, x, y):
  if (x < 0 or y < 0 or x >= width or y >= height or map[x][y] >= 1):
    return 0;

  map[x][y] = 2
  total = 1
  total += fill(map,  width, height, x + 1, y)
  total += fill(map,  width, height, x - 1, y)
  total += fill(map,  width, height, x, y + 1)
  total += fill(map,  width, height, x, y - 1)
  return total;

def setBound(map, length_map, opp, game_state):
  #Set bound for other snake 
  myself = game_state["you"]
  for i in range(len(opp)):
    bod = opp[i]["body"]
    for j in bod:
      x = j["x"]
      y = j["y"]
      map[x][y] = 1
      if (opp[i]["id"] != myself["id"]):
         length_map[x][y] = opp[i]["length"]
  
  return map, length_map


def score(game_state, head, moves, map):
  #for all moves with a score not = '-inf' make the move and look for snakes that can get there in one move (snakes around the new square) and score based on length and space available
  # add a scoring based on average space available after making a move
  avg = {"up":0, "down":0, "left":0, "right":0}
  for move, score in moves.items():
    if score>MIN_SCORE:
      if move == "up":
            x = head["x"]
            y = head["y"] + 1
            offsets = [[1,0], [-1,0], [0,1]]
      if move == "down":
            x = head["x"]
            y = head["y"] - 1
            offsets = [[1,0], [-1,0], [0,-1]]
      if move == "left":
            x = head["x"] - 1
            y = head["y"] 
            offsets = [[0,1], [0,-1], [-1,0]]
      if move == "right":
            x = head["x"] + 1
            y = head["y"] 
            offsets = [[0,1], [0,-1], [1,0]]
      # if game_state["you"]["length"]>15 and (x == 0 or x == game_state["board"]["width"]-1 or y == 0 or y == game_state["board"]["height"]-1):
      #   moves[move]-=0.4
      for snake in game_state["board"]["snakes"]:
            if snake["id"] == game_state["you"]["id"] : continue
            enemy_head = snake["head"]
            for idx in offsets:
                #print('idx: ', idx , 'move: ', move , 'enemy_head: ', enemy_head)
                o_x = idx[0] + x
                o_y = idx[1] + y
                if (enemy_head["x"] == o_x and enemy_head["y"] == o_y) :
                    if snake["length"] > game_state["you"]["length"] :
                        moves[move] -= LARGER_SNAKE_DANGER
                    elif snake["length"] == game_state["you"]["length"] :
                        moves[move] -= SAME_SNAKE_DANGER
                    else :
                    ## if we want to be agressive and attack the weaker snake
                        moves[move] += SMALLER_SNAKE_REWARD
      cpy_map = [row[:] for row in map]
      cpy_map[x][y]=1
      cpy_map[game_state["you"]["body"][-1]["x"]][game_state["you"]["body"][-1]["y"]] = 0
      spaces = floodFill(cpy_map, game_state["board"]["width"], game_state["board"]["height"], x, y)
      avg[move] = max([space for move, space in spaces.items()])
  print(f"average spaces {avg}")
  max_space = max([space for move, space in avg.items()])
  largest = [move for move, space in avg.items() if space==max_space]
  for move in largest:
    moves[move]+=1
  return moves



  
if __name__ == "__main__":
    from server import run_server

    run_server({
        "info": info, 
        "start": start, 
        "move": move, 
        "end": end
    })
  
# step 1-4: Abhijoy (done)
# Step 2-3 Yucheng   (done)
# Flood-fill : Yucheng (done)
# Map:  Yu Cheng    2D map of boundaries  (done)
# Food finding: Abhijoy (done)
# Move scoring with one step look-ahead: tbd (Abhijoy: added skeleton)
# common kill patterns: (Abhijoy: added edge kill condition when 2 snakes are left)
# Additional tail cases
# Improve space lookahead

  
#TODO
# Balancing
# Clean up code
# Avoid food beside big snakes (check if targeted food is close to other snake)
# Force kill on edge (if no edge danger, force snake to move toward edge)



