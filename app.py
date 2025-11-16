import cv2
import mediapipe as mp
import pyautogui
import time

# Mediapipe Hands setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)

# Swipe detection variables
prev_x, prev_y = None, None
gesture_cooldown = 3      # seconds before another gesture can be detected
last_gesture_time = 0

SWIPE_THRESHOLD = 80      # pixels
DOWN_THRESHOLD = 80       # pixels

print("Gesture Control Started. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            # Get center point of hand
            h, w, _ = frame.shape
            cx = int(handLms.landmark[9].x * w)   # landmark 9 = center-ish of palm
            cy = int(handLms.landmark[9].y * h)

            # Draw for debug
            cv2.circle(frame, (cx, cy), 10, (0,255,0), -1)
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            # Only detect gesture if enough time has passed
            if time.time() - last_gesture_time > gesture_cooldown:

                if prev_x is not None and prev_y is not None:
                    dx = cx - prev_x
                    dy = cy - prev_y

                    # Swipe Right → Next Slide
                    if dx > SWIPE_THRESHOLD:
                        print("Swipe Right → Next Slide")
                        pyautogui.press("right")
                        last_gesture_time = time.time()

                    # Swipe Left → Previous Slide
                    elif dx < -SWIPE_THRESHOLD:
                        print("Swipe Left → Previous Slide")
                        pyautogui.press("left")
                        last_gesture_time = time.time()

                    # Swipe Down → Exit Presentation
                    elif dy > DOWN_THRESHOLD:
                        print("Swipe Down → Exit Presentation")
                        pyautogui.press("esc")
                        last_gesture_time = time.time()

                prev_x, prev_y = cx, cy

    cv2.imshow("Gesture Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
