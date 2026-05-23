import cv2
import mediapipe as mp
import numpy as np
import math
import random

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)

cap = cv2.VideoCapture(0)

cube_size = 80
cube_pos = (300, 300)
health = 100
score = 0

enemies = []


def distance(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])


while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame,1)

    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    hand_centers = []

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            ix = int(hand_landmarks.landmark[8].x * w)
            iy = int(hand_landmarks.landmark[8].y * h)

            tx = int(hand_landmarks.landmark[4].x * w)
            ty = int(hand_landmarks.landmark[4].y * h)

            cx = (ix + tx)//2
            cy = (iy + ty)//2

            hand_centers.append((cx, cy))

    # 🎯 control cube with first hand
    if len(hand_centers) >= 1:
        cube_pos = hand_centers[0]

    # 👾 spawn enemies
    if random.randint(0,20) == 0:
        enemies.append([
            random.randint(0,w),
            0,
            random.uniform(-2,2),
            random.uniform(2,5)
        ])

    # 🔄 move enemies
    new_enemies = []
    for e in enemies:
        e[0] += e[2]
        e[1] += e[3]

        # collision with cube
        if distance((e[0],e[1]), cube_pos) < cube_size:
            health -= 5
            continue

        # second hand destroys enemies
        if len(hand_centers) == 2:
            if distance((e[0],e[1]), hand_centers[1]) < 60:
                score += 1
                continue

        # draw enemy
        cv2.circle(frame, (int(e[0]), int(e[1])), 10, (0,0,255), -1)

        new_enemies.append(e)

    enemies = new_enemies

    # draw cube (simple square for clarity)
    x, y = cube_pos
    s = cube_size

    cv2.rectangle(frame, (x-s, y-s), (x+s, y+s), (255,255,255), 2)

    # UI
    cv2.putText(frame, f"Health: {health}", (10,30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.putText(frame, f"Score: {score}", (10,70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)

    # game over
    if health <= 0:
        cv2.putText(frame, "GAME OVER", (200,300),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 4)

    cv2.imshow("Aadya Cube Game", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
