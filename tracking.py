import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

# Configurações do cursor e fixação
sensitivity = 6.0
history_length = 10
x_history = []
y_history = []

# Fixação
FIXATION_TIME = 1.2
FIXATION_DELAY = 0.3
FIXATION_TOLERANCE = 10
fixation_start_time = None
fixation_ready = False
last_cursor_position = None
click_enabled = False  # estado inicial: clique desativado

# Boca aberta
MOUTH_OPEN_THRESHOLD = 0.06
mouth_open = False  # controle de transição

pyautogui.moveTo(screen_w / 2, screen_h / 2)

def moving_average(values, new_value, length):
    values.append(new_value)
    if len(values) > length:
        values.pop(0)
    return np.mean(values)

def is_mouth_open(landmarks):
    top_lip = landmarks[13]
    bottom_lip = landmarks[14]
    return abs(top_lip.y - bottom_lip.y) > MOUTH_OPEN_THRESHOLD

while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape

    # Indicador de rastreamento
    cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1)
    status_text = "Clique ATIVADO" if click_enabled else "Clique DESATIVADO"
    status_color = (0, 255, 0) if click_enabled else (0, 100, 255)
    cv2.putText(frame, status_text, (50, 37), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)

    if landmark_points:
        landmarks = landmark_points[0].landmark

        # Detectar abertura da boca para alternar modo
        if is_mouth_open(landmarks):
            if not mouth_open:
                click_enabled = not click_enabled  # alterna o estado
                mouth_open = True
        else:
            mouth_open = False

        # Movimento do cursor
        for id, landmark in enumerate(landmarks[474:478]):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0))
            if id == 1:
                screen_x = screen_w / 2 + (landmark.x - 0.5) * screen_w * sensitivity
                screen_y = screen_h / 2 + (landmark.y - 0.5) * screen_h * sensitivity
                screen_x = moving_average(x_history, screen_x, history_length)
                screen_y = moving_average(y_history, screen_y, history_length)
                screen_x = min(screen_w, max(0, screen_x))
                screen_y = min(screen_h, max(0, screen_y))
                pyautogui.moveTo(screen_x, screen_y)

                # Retícula visual
                ret_x = int(landmark.x * frame_w)
                ret_y = int(landmark.y * frame_h)
                cv2.circle(frame, (ret_x, ret_y), 10, (255, 255, 255), 2)
                cv2.circle(frame, (ret_x, ret_y), 6, (255, 0, 0), -1)

                # FIXAÇÃO (só se clique estiver ativado)
                if click_enabled:
                    current_pos = (screen_x, screen_y)

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
                                    cv2.circle(frame, (ret_x, ret_y), 40, (0, 255, 255), -1)
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
cv2.destroyAllWindows()