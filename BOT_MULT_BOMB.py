# -*- coding: utf-8 -*-    
from socket import timeout
from cv2 import cv2
from os import listdir
from src.logger import logger, loggerMapClicked
from random import randint
from random import random
import pygetwindow
import numpy as np
import mss
import pyautogui
import time
import sys
import yaml

cat = """ INICIANDO FARM MULTI ACCOUNT  ... """

print('\n',cat,'\n')
timeout(2)

if __name__ == '__main__':
    stream = open("config.yaml", 'r')
    c = yaml.safe_load(stream)

ct = c['threshold']
ch = c['home']

if not ch['enable']:
    print('\n')

pause = c['time_intervals']['interval_between_moviments']
pyautogui.PAUSE = pause
pyautogui.FAILSAFE = False
hero_clicks = 0
login_attempts = 0
last_log_is_progress = False

def addRandomness(n, randomn_factor_size=None):
    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n
    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    return int(randomized_n)

def moveToWithRandomness(x,y,t):
    pyautogui.moveTo(addRandomness(x,10),addRandomness(y,10),t+random()/2)

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def load_images():
    file_names = listdir('./targets/')
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)
    return targets

images = load_images()

def loadHeroesToSendHome():
    file_names = listdir('./targets/heroes-to-send-home')
    heroes = []
    for file in file_names:
        path = './targets/heroes-to-send-home/' + file
        heroes.append(cv2.imread(path))
    print('>>---> %d heroes that should be sent home loaded' % len(heroes))
    return heroes

if ch['enable']:
    home_heroes = loadHeroesToSendHome()

# go_work_img = cv2.imread('targets/go-work.png')
# commom_img = cv2.imread('targets/commom-text.png')
# arrow_img = cv2.imread('targets/go-back-arrow.png')
# hero_img = cv2.imread('targets/hero-icon.png')
# x_button_img = cv2.imread('targets/x.png')
# teasureHunt_icon_img = cv2.imread('targets/treasure-hunt-icon.png')
# ok_btn_img = cv2.imread('targets/ok.png')
# connect_wallet_btn_img = cv2.imread('targets/connect-wallet.png')
# select_wallet_hover_img = cv2.imread('targets/select-wallet-1-hover.png')
# select_metamask_no_hover_img = cv2.imread('targets/select-wallet-1-no-hover.png')
# sign_btn_img = cv2.imread('targets/select-wallet-2.png')
# new_map_btn_img = cv2.imread('targets/new-map.png')
# green_bar = cv2.imread('targets/green-bar.png')
full_stamina = cv2.imread('targets/full-stamina.png')
robot = cv2.imread('targets/robot.png')
# puzzle_img = cv2.imread('targets/puzzle.png')
# piece = cv2.imread('targets/piece.png')
slider = cv2.imread('targets/slider.png')

def show(rectangles, img = None):
    if img is None:
        with mss.mss() as sct:
           monitor = sct.monitors[0]
           img = np.array(sct.grab(monitor))
    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255,255), 2)
    cv2.imshow('img',img)
    cv2.waitKey(0)

def clickBtn(img,name=None, timeout=3, threshold = ct['default']):
    logger(None, progress_indicator=True)
    if not name is None:
        pass
    start = time.time()
    while(True):
        matches = positions(img, threshold=threshold)
        if(len(matches)==0):
            hast_timed_out = time.time()-start > timeout
            if(hast_timed_out):
                if not name is None:
                    pass
                return False
            continue

        x,y,w,h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        # mudar moveto pra w randomness
        moveToWithRandomness(pos_click_x,pos_click_y,1)
        pyautogui.click()
        return True
        print("THIS SHOULD NOT PRINT")


def printSreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        return sct_img[:,:,:3]

def positions(target, threshold=ct['default'],img = None):
    if img is None:
        img = printSreen()
    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]
    yloc, xloc = np.where(result >= threshold)
    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])
    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles

def scroll():
    commoms = positions(images['commom-text'], threshold = ct['commom'])
    if (len(commoms) == 0):
        return
    x,y,w,h = commoms[len(commoms)-1]
    moveToWithRandomness(x,y,1)
    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0,-c['click_and_drag_amount'],duration=1, button='left')
    timeout(2)

def clickButtons():
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    for (x, y, w, h) in buttons:
        moveToWithRandomness(x+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        if hero_clicks > 20:
            return
    return len(buttons)

def isHome(hero, buttons):
    y = hero[1]
    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True

def isWorking(bar, buttons):
    y = bar[1]
    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True

def clickGreenBarButtons():
    offset = 150
    green_bars = positions(images['green-bar'], threshold=ct['green_bar'])
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    not_working_green_bars = []
    for bar in green_bars:
        if not isWorking(bar, buttons):
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        logger('ENCONTRADO HEROIS COM ESTAMINA VERDE')
        pass
    for (x, y, w, h) in not_working_green_bars:
        moveToWithRandomness(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        if hero_clicks > 20:
            return
    return len(not_working_green_bars)

def clickFullBarButtons():
    offset = 150
    full_bars = positions(images['full-stamina'], threshold=ct['default'])
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    not_working_full_bars = []
    for bar in full_bars:
        if not isWorking(bar, buttons):
            not_working_full_bars.append(bar)
            pass
    if len(not_working_full_bars) > 0:
        logger('ENCONTRADO HEROIS COM ESTAMINA FULL')
    for (x, y, w, h) in not_working_full_bars:
        pass
        moveToWithRandomness(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
    return len(not_working_full_bars)

def goToHeroes():
    if clickBtn(images['go-back-arrow']):
        global login_attempts
        login_attempts = 0
        pass
    clickBtn(images['hero-icon'])

def goToGame():
    logger('ENVIANDO PARA O MAPA ...')
    clickBtn(images['x'])
    clickBtn(images['x'])
    timeout(5)
    clickBtn(images['treasure-hunt-icon'])

def refreshHeroesPositions():
    logger('REINCIANDO POSI????ES DO HEROIS')
    clickBtn(images['go-back-arrow'])
    clickBtn(images['treasure-hunt-icon'])

def login():
    global login_attempts
    logger('VERIFICANDO SE A CONTA SE ENCONTRA DESCONECTADA ...')
    if clickBtn(images['connect-wallet'], name='connectWalletBtn', timeout = 5):
        logger('BOT??O DA CARTEIRA ENCONTRADO, REALIANDO LOGIN ...')
        login_attempts = login_attempts + 1
        if login_attempts > 3:
            login_attempts = 0
            pyautogui.hotkey('ctrl','f5')
            logger('REFRESH PAGE ...')
            timeout(5)
            login()
            pass
    if clickBtn(images['connect-login-bomb'], timeout = 5):
        login_attempts = login_attempts + 1
        timeout(2)
        logger('CONECTANDO ...')
        pass
    if clickBtn(images['ok'], name='okBtn', timeout=5):
        pass

def sendHeroesHome():
    if not ch['enable']:
        return
    heroes_positions = []
    for hero in home_heroes:
        hero_positions = positions(hero, threshold=ch['hero_threshold'])
        if not len (hero_positions) == 0:
            hero_position = hero_positions[0]
            heroes_positions.append(hero_position)
    n = len(heroes_positions)
    if n == 0:
        print('No heroes that should be sent home found.')
        return
    print(' %d heroes that should be sent home found' % n)
    go_home_buttons = positions(images['send-home'], threshold=ch['home_button_threshold'])
    go_work_buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    for position in heroes_positions:
        if not isHome(position,go_home_buttons):
            print(isWorking(position, go_work_buttons))
            if(not isWorking(position, go_work_buttons)):
                print ('hero not working, sending him home')
                moveToWithRandomness(go_home_buttons[0][0]+go_home_buttons[0][2]/2,position[1]+position[3]/2,1)
                pyautogui.click()
                pass
            else:
                print ('hero working, not sending him home(no dark work button)')
        else:
            print('hero already home, or home full(no dark home button)')

def refreshHeroes():
    logger('PROCURANDO HEROIS PARA REALIZAR O TRABALHO ...')
    goToHeroes()
    if c['select_heroes_mode'] == "full":
        logger('ENVIANDO HEROIS PARA TRABALHAR COM ESTAMINA CHEIA ...', 'full')
        pass
    if c['select_heroes_mode'] == "green":
        logger('ENVIANDO HEROIS PARA TRABALHAR COM ESTAMINA VERDE ...', 'green')
        pass
    else:
        logger('ENVIANDO TODOS OS HEROIS PARA O TRABALHO ...', 'green')
    buttonsClicked = 1
    empty_scrolls_attempts = c['scroll_attemps']
    while(empty_scrolls_attempts >0):
        if c['select_heroes_mode'] == 'full':
            buttonsClicked = clickFullBarButtons()
            if buttonsClicked == 0:
                empty_scrolls_attempts = empty_scrolls_attempts - 1
                scroll()
                pass
        if c['select_heroes_mode'] == 'green':
            buttonsClicked = clickGreenBarButtons()
            if buttonsClicked == 0:
                empty_scrolls_attempts = empty_scrolls_attempts - 1
                scroll()
                pass
        else:
            buttonsClicked = clickButtons()
            if buttonsClicked == 0:
                empty_scrolls_attempts = empty_scrolls_attempts - 1
                scroll()
                pass
        sendHeroesHome()
    goToGame()

def main():
    timeout(10)
    t = c['time_intervals']
    windows = []
    for w in pygetwindow.getWindowsWithTitle('bombcrypto'):
        windows.append({
            "window": w,
            "login" : 0,
            "heroes" : 0,
            "new_map" : 0,
            "refresh_heroes" : 0
            })
    while True:
        timeout(10)
        now = time.time()
        for last in windows:
            last['window'].activate()
            if now - last['login'] > addRandomness(t['check_for_login'] * 120):
                sys.stdout.flush()
                last["login"] = now
                login()
                timeout(5)
                goToGame()
                timeout(20)
                pass
                if now - last['new_map'] > t['check_for_new_map_button']:
                    last['new_map'] = now
                    if clickBtn(images['new-map']):
                        loggerMapClicked();
                        pass
                if now - last['heroes'] > addRandomness(t['send_heroes_for_work'] * 120):
                    timeout(10)
                    last['heroes'] = now 
                    refreshHeroes()
                    pass
                if last in windows:
                    timeout(10)
                    last['window'].activate()
                    pass
            logger(None, progress_indicator=True)
            sys.stdout.flush()
            timeout(5)
main()
