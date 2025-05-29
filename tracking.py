import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import json
import os
import subprocess
import sys

pyautogui.FAILSAFE = False

# Caminho do arquivo de configuração
CONFIG_PATH = os.path.join("settings", "config.json")
CLICK_STATE_PATH = os.path.join("settings", "click_state.json")

# Função para salvar o estado atual do clique em um arquivo
def save_click_state(state):
    try:
        with open(CLICK_STATE_PATH, 'w') as f:
            json.dump({"click_enabled": state}, f)
    except Exception as e:
        print("Erro ao salvar estado do clique:", e)

# Função para carregar configurações do JSON
def load_config():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                data = json.load(f)
                return float(data.get("sensitivity", 6.0)), float(data.get("fixation_time", 1.2))
    except json.JSONDecodeError:
        print("⚠️ AVISO: config.json está vazio ou inválido. Usando valores padrão.")
    return 6.0, 1.2

# Inicialização
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

# Carrega configurações do usuário
sensitivity, FIXATION_TIME = load_config()

history_length = 10
x_history = []
y_history = []

FIXATION_DELAY = 0.3
FIXATION_TOLERANCE = 10
fixation_start_time = None
fixation_ready = False
last_cursor_position = None
click_enabled = False

MOUTH_OPEN_THRESHOLD = 0.06
mouth_open = False

menu_fixation_start = None
menu_progress_proc = None
MENU_FIXATION_DURATION = 3.0
menu_triggered = False
menu_open = False
menu_proc = None

pyautogui.moveTo(screen_w / 2, screen_h / 2)

save_click_state(click_enabled)  # Estado inicial

# Inicia o overlay Electron automaticamente
try:
    overlay_dir = os.path.join(os.getcwd(), "overlay-electron")
    overlay_proc = subprocess.Popen(["npm", "start"], cwd=overlay_dir)
except Exception as e:
    print("Erro ao iniciar overlay Electron:", e)

def moving_average(values, new_value, length):
    values.append(new_value)
    if len(values) > length:
        values.pop(0)
    return np.mean(values)

def is_mouth_open(landmarks):
    top_lip = landmarks[13]
    bottom_lip = landmarks[14]
    return abs(top_lip.y - bottom_lip.y) > MOUTH_OPEN_THRESHOLD

def open_settings_menu():
    global menu_open, menu_proc
    menu_proc = subprocess.Popen([sys.executable, "settings_window.py"])
    menu_open = True

def show_progress_indicator():
    return subprocess.Popen([sys.executable, "menu_indicator.py"])

while True:
    if menu_open and menu_proc and menu_proc.poll() is not None:
        menu_open = False

    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape

    if landmark_points:
        landmarks = landmark_points[0].landmark

        if is_mouth_open(landmarks):
            if not mouth_open:
                click_enabled = not click_enabled
                save_click_state(click_enabled)
                mouth_open = True
        else:
            mouth_open = False

        for id, landmark in enumerate(landmarks[474:478]):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            if id == 1:
                screen_x = screen_w / 2 + (landmark.x - 0.5) * screen_w * sensitivity
                screen_y = screen_h / 2 + (landmark.y - 0.5) * screen_h * sensitivity
                screen_x = moving_average(x_history, screen_x, history_length)
                screen_y = moving_average(y_history, screen_y, history_length)
                screen_x = min(screen_w, max(0, screen_x))
                screen_y = min(screen_h, max(0, screen_y))
                pyautogui.moveTo(screen_x, screen_y)

                ret_x = int(landmark.x * frame_w)
                ret_y = int(landmark.y * frame_h)

                current_pos = (screen_x, screen_y)

                in_corner = screen_x > screen_w * 0.9 and screen_y < screen_h * 0.1

                if click_enabled and in_corner and not menu_open:
                    if not menu_fixation_start and not menu_triggered:
                        menu_fixation_start = time.time()
                        menu_progress_proc = show_progress_indicator()
                    elif not menu_triggered and time.time() - menu_fixation_start >= MENU_FIXATION_DURATION:
                        menu_triggered = True
                        if menu_progress_proc:
                            menu_progress_proc.kill()
                        open_settings_menu()
                        menu_fixation_start = None
                        menu_progress_proc = None
                else:
                    if menu_fixation_start or menu_triggered:
                        menu_fixation_start = None
                        if menu_progress_proc:
                            menu_progress_proc.kill()
                            menu_progress_proc = None
                        if not in_corner:
                            menu_triggered = False

                if click_enabled:
                    if last_cursor_position:
                        dist = np.linalg.norm(np.array(current_pos) - np.array(last_cursor_position))
                        if dist < FIXATION_TOLERANCE:
                            if fixation_start_time is None:
                                fixation_start_time = time.time()
                                fixation_ready = False
                            elif not fixation_ready:
                                if time.time() - fixation_start_time >= FIXATION_DELAY:
                                    fixation_ready = True
                                    fixation_start_time = time.time()
                            elif fixation_ready:
                                if time.time() - fixation_start_time >= FIXATION_TIME:
                                    pyautogui.click()
                                    fixation_start_time = None
                                    fixation_ready = False
                        else:
                            fixation_start_time = None
                            fixation_ready = False

                    last_cursor_position = current_pos

    cv2.imshow('FeelGaze - Eye Tracking', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()

# Encerra o processo do overlay ao sair
if 'overlay_proc' in locals():
    overlay_proc.kill()

cv2.destroyAllWindows()