import random
import typing
from collections import deque

def info() -> typing.Dict:
    return {
        "apiversion": "1",
        "author": "oliviamrkw", # name: mr snake
        "color": "#ffffff",
        "head": "tongue",
        "tail": "weight"
    }

def start(game_state: typing.Dict):
    print("GAME START")

def end(game_state: typing.Dict):
    print("GAME OVER\n")

def move(game_state: typing.Dict) -> typing.Dict:
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}
    my_head = game_state["you"]["body"][0]
    my_body = game_state["you"]["body"]
    opponents = game_state["board"]["snakes"]
    food = game_state["board"]["food"]
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    def new_position(head, direction):
        if direction == "up":
            return {"x": head["x"], "y": head["y"] + 1}
        elif direction == "down":
            return {"x": head["x"], "y": head["y"] - 1}
        elif direction == "left":
            return {"x": head["x"] - 1, "y": head["y"]}
        elif direction == "right":
            return {"x": head["x"] + 1, "y": head["y"]}

    # wall collisions
    if my_head["x"] == 0:
        is_move_safe["left"] = False
    if my_head["x"] == board_width - 1:
        is_move_safe["right"] = False
    if my_head["y"] == 0:
        is_move_safe["down"] = False
    if my_head["y"] == board_height - 1:
        is_move_safe["up"] = False

    # body collisions
    for part in my_body[1:]:
        for move in list(is_move_safe.keys()):
            if new_position(my_head, move) == part:
                is_move_safe[move] = False

    # opponent collisions
    for snake in opponents:
        for part in snake["body"]:
            for move in list(is_move_safe.keys()):
                if new_position(my_head, move) == part:
                    is_move_safe[move] = False

    # flood fill algorithm
    def flood_fill(start, blocked):
        queue = deque([start])
        visited = set()
        while queue:
            current = queue.popleft()
            if tuple(current.values()) in visited or tuple(current.values()) in blocked:
                continue
            visited.add(tuple(current.values()))
            for direction in ["up", "down", "left", "right"]:
                neighbor = new_position(current, direction)
                if 0 <= neighbor["x"] < board_width and 0 <= neighbor["y"] < board_height:
                    queue.append(neighbor)
        return len(visited)

    blocked_positions = set(tuple(part.values()) for snake in opponents for part in snake["body"])
    blocked_positions.update(tuple(part.values()) for part in my_body)

    for move in list(is_move_safe.keys()):
        next_position = new_position(my_head, move)
        if is_move_safe[move] and flood_fill(next_position, blocked_positions) < len(my_body):
            is_move_safe[move] = False

    print(f"Safe moves after flood-fill: {is_move_safe}")

    # food prioritization
    if food:
        closest_food = min(food, key=lambda f: abs(f["x"] - my_head["x"]) + abs(f["y"] - my_head["y"]))
        food_direction = None
        if closest_food["x"] < my_head["x"]:
            food_direction = "left"
        elif closest_food["x"] > my_head["x"]:
            food_direction = "right"
        elif closest_food["y"] < my_head["y"]:
            food_direction = "down"
        elif closest_food["y"] > my_head["y"]:
            food_direction = "up"
        if food_direction in is_move_safe and is_move_safe[food_direction]:
            print(f"Food found at {closest_food}, moving {food_direction}")
            return {"move": food_direction}

    # safe moves
    safe_moves = [move for move, safe in is_move_safe.items() if safe]
    if not safe_moves:
        print(f"Turn {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    next_move = random.choice(safe_moves)
    print(f"Turn {game_state['turn']}: Choosing random safe move {next_move}")
    return {"move": next_move}

if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
