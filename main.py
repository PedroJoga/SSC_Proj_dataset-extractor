import pyautogui
from enum import Enum
from pynput import keyboard
from win10toast import ToastNotifier
import re
import os
import warnings

warnings.filterwarnings("ignore")

class Role(Enum):
    TOP = "top"
    JUNGLE = "jungle"
    MID = "mid"
    ADC = "adc"
    SUPPORT = "support"

class Team(Enum):
    RED = "red"
    BLUE = "blue"

mini_map_position_x = 0
mini_map_position_y = 0
MINI_MAP_OFFSET_X = 277
MINI_MAP_OFFSET_Y = 277

TEAM_SIDE_DELIMITER = 350 # delimiter based on "mini_map_position_y"
PLAYER1_DELIMITER = 46 # delimiter based on "mini_map_position_x"
PLAYER2_DELIMITER = 108 # delimiter based on "mini_map_position_x"
PLAYER3_DELIMITER = 171 # delimiter based on "mini_map_position_x"
PLAYER4_DELIMITER = 233 # delimiter based on "mini_map_position_x"

pressed = set()

counter = 1
selected_role = None

EMPTY_LIST = [None, None, None, None, None]
red_team_roles = EMPTY_LIST.copy() # [<player1>, <player2>, <player3>, <player4>, <player5>]
red_team_images = EMPTY_LIST.copy()
blue_team_roles = EMPTY_LIST.copy()
blue_team_images = EMPTY_LIST.copy()
EMPTY_GLOBAL_MATCH_DATA = {"image": "", "time": "", "win_team": ""}
global_match_data = EMPTY_GLOBAL_MATCH_DATA.copy()

IMAGE_EXTENSION = ".jpg"
SAVE_DATASET_DIR = fr"./dataset/"
TURN_OFF_NOTIFICATIONS = True

def find_last_match(directory):
    pattern = re.compile(r'^Match(\d+)\b')  # Captura "Match" seguido de números

    great_num = -1
    for file_name in os.listdir(directory):
        match = pattern.match(file_name)
        if match:
            num = int(match.group(1))
            if num > great_num:
                great_num = num

    return great_num if great_num != -1 else None

def notify(message: str, tittle: str = "\tNotification", duration: int = 1, turn_off: bool = TURN_OFF_NOTIFICATIONS) -> None:
    print("\t" + tittle + ": " + message)
    if turn_off:
        return
    toaster = ToastNotifier()
    toaster.show_toast(tittle, message, duration=duration, threaded=True)

def show_current_data():
    global global_match_data, red_team_roles, blue_team_roles

    col_titles = ["Player 1", "Player 2", "Player 3", "Player 4", "Player 5"]
    row_titles = ["Red Team", "Blue Team"]

    col_width = 9
    def format_row(cells):
        return "| " + " | ".join(str(cell if cell is not None else "").ljust(col_width) for cell in cells) + " |"
    
    header = format_row([""] + col_titles)
    separator = "+" + "+".join(["-" * (col_width + 2)] * (len(col_titles) + 1)) + "+"

    print(separator)
    print(fr"Win team: {global_match_data["win_team"]} | Time: {global_match_data["time"]} min.")
    print(separator)
    print(header)
    print(separator)
    print(format_row([row_titles[1]] + blue_team_roles))
    print(format_row([row_titles[0]] + red_team_roles))
    print(separator)


def take_screenshot(x, y, x_offset=MINI_MAP_OFFSET_X, y_offset=MINI_MAP_OFFSET_Y, save_as='screenshot.png', return_image = False):

    image = pyautogui.screenshot(region=(x, y, x_offset, y_offset))
    if return_image:
        return image
    image.save(save_as)

def get_cursor_position():
    x, y = pyautogui.position()
    return x, y

def run():
    global blue_team_roles, red_team_roles, selected_role, mini_map_position_x, mini_map_position_y, blue_team_images, red_team_images, global_match_data
    if not selected_role:
        notify("Role not defined")
        return

    x, y = get_cursor_position()   

    if y < mini_map_position_y + TEAM_SIDE_DELIMITER:
        # blue team  
        selected_team_roles = blue_team_roles
        selected_team_images = blue_team_images
    else:
        selected_team_roles = red_team_roles
        selected_team_images = red_team_images

    image = take_screenshot(mini_map_position_x, mini_map_position_y, return_image=True)

    if x < mini_map_position_x + PLAYER1_DELIMITER:
        #player1
        selected_team_roles[0] = selected_role
        selected_team_images[0] = image.copy()
    elif x < mini_map_position_x + PLAYER2_DELIMITER:
        #player2
        selected_team_roles[1] = selected_role
        selected_team_images[1] = image.copy()
    elif x < mini_map_position_x + PLAYER3_DELIMITER:
        #player3
        selected_team_roles[2] = selected_role
        selected_team_images[2] = image.copy()
    elif x < mini_map_position_x + PLAYER4_DELIMITER:
        #player4
        selected_team_roles[3] = selected_role
        selected_team_images[3] = image.copy()
    else:
        #player5
        selected_team_roles[4] = selected_role
        selected_team_images[4] = image.copy()

def save_data():
    global counter, red_team_roles, red_team_images, blue_team_roles, blue_team_images, global_match_data

    if None in red_team_roles:
        notify("Red team role incomplete")
        show_current_data()
        return

    if None in red_team_images:
        notify("Red team images incomplete")
        show_current_data()
        return
    
    if None in blue_team_roles:
        notify("Blue team role incomplete")
        show_current_data()
        return
    
    if None in blue_team_images:
        notify("Blue team images incomplete")
        show_current_data()
        return
    
    if any(value == "" for value in global_match_data.values()):
        notify("Global match data incomplete")
        show_current_data()
        return

    global_label = fr"Match{counter} Glob {global_match_data["time"]} {global_match_data["win_team"]}{IMAGE_EXTENSION}"
    global_match_data["image"].save(SAVE_DATASET_DIR + global_label)

    for i in range (5):
        if global_match_data["win_team"] == Team.BLUE.value:
            player_label = fr"Match{counter} Ind {True} {blue_team_roles[i]}{IMAGE_EXTENSION}"
            blue_team_images[i].save(SAVE_DATASET_DIR + player_label)
            player_label = fr"Match{counter} Ind {False} {red_team_roles[i]}{IMAGE_EXTENSION}"
            red_team_images[i].save(SAVE_DATASET_DIR + player_label)
        else:
            player_label = fr"Match{counter} Ind {False} {blue_team_roles[i]}{IMAGE_EXTENSION}"
            blue_team_images[i].save(SAVE_DATASET_DIR + player_label)
            player_label = fr"Match{counter} Ind {True} {red_team_roles[i]}{IMAGE_EXTENSION}"
            red_team_images[i].save(SAVE_DATASET_DIR + player_label)
    
    notify(rf"Iteration {counter} completed, going to next...")
    counter += 1
        
def on_press(key):
    global mini_map_position_x, mini_map_position_y, selected_role, global_match_data, red_team_roles, blue_team_roles, red_team_images, blue_team_images
    if pressed:
        return
    pressed.add(key)

    # save dataset =======================================
    if pressed == {keyboard.Key.enter}:
        save_data()
        return
    
    # define mini-map position and take global map screenshot =======================================
    if pressed == {keyboard.Key.ctrl_l}:
        # set default values
        selected_role = None
        red_team_roles = EMPTY_LIST.copy()
        blue_team_roles = EMPTY_LIST.copy()
        red_team_images = EMPTY_LIST.copy()
        blue_team_images = EMPTY_LIST.copy()

        mini_map_position_x, mini_map_position_y = get_cursor_position()
        image = take_screenshot(mini_map_position_x, mini_map_position_y, return_image=True)
        global_match_data = EMPTY_GLOBAL_MATCH_DATA.copy()
        global_match_data["image"] = image
        notify(fr"New mini-map position defined {mini_map_position_x}x{mini_map_position_y}")
        return
    
    # reset time =======================================
    if pressed == {keyboard.Key.left}:
        global_match_data["time"] = ""
        notify(fr"Time reset")
        return
    
    # reset roles and take global map screenshot =======================================
    if pressed == {keyboard.Key.backspace}:
        # set default values
        selected_role = None
        red_team_roles = EMPTY_LIST.copy()
        blue_team_roles = EMPTY_LIST.copy()
        red_team_images = EMPTY_LIST.copy()
        blue_team_images = EMPTY_LIST.copy()

        image = take_screenshot(mini_map_position_x, mini_map_position_y, return_image=True)
        global_match_data = EMPTY_GLOBAL_MATCH_DATA.copy()
        global_match_data["image"] = image
        notify(fr"New dataset initiated")
        return

    # define win team =======================================
    if pressed == {keyboard.Key.down}:
        global_match_data["win_team"] = Team.RED.value
        notify(fr"{Team.RED.value} Team Wins", "Win team defined")
        return

    # define win team =======================================
    if pressed == {keyboard.Key.up}:
        global_match_data["win_team"] = Team.BLUE.value
        notify(fr"{Team.BLUE.value} Team Wins", "Win team defined")
        return

    
    if hasattr(key, 'char') and key.char is not None:
        # Verifica se uma tecla de letra (a-z) foi pressionada
        # select role and take players screenshots =======================================
        if key.char.isalpha():
            letter = key.char.lower()
            if letter == 'a':
                selected_role = Role.TOP.value
            elif letter == 's':
                selected_role = Role.JUNGLE.value
            elif letter == 'd':
                selected_role = Role.MID.value
            elif letter == 'f':
                selected_role = Role.ADC.value
            elif letter == 'g':
                selected_role = Role.SUPPORT.value
            
            if letter in ['a', 's', 'd', 'f', 'g']:
                run()
                show_current_data()
                notify(rf"Role selected: {selected_role}", "Role selection")
            return
        
        # Verifica se uma tecla numérica (0-9) foi pressionada
        if key.char.isdigit():
            global_match_data["time"] = global_match_data["time"] + str(key.char)
            notify(rf"Time updated: {global_match_data["time"]}", "Time selection")
            return

def on_release(key):
    if key == keyboard.Key.esc: # esc to stop
        return False
    if key in pressed:
        pressed.remove(key)


if __name__ == "__main__":
    counter = find_last_match(SAVE_DATASET_DIR)
    if not counter:
        counter = 1

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
