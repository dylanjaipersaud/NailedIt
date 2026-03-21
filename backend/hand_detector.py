import cv2
import mediapipe as mp
from mediapipe import ImageFormat
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarkerOptions, HandLandmarker, RunningMode
import math, time

# Initialize hand capturing objects from MediaPipe
# Base model from https://developers.google.com/mediapipe/solutions/vision/hand_landmarker
model_path = "hand_landmarker.task"

base_options = BaseOptions(model_asset_path=model_path)
options = HandLandmarkerOptions(base_options=base_options, num_hands=2, running_mode=RunningMode.VIDEO)
landmarker = HandLandmarker.create_from_options(options=options)

# mp_hands = mp.solutions.hands
# hands = mp_hands.Hands(
#     max_num_hands=1,
#     min_detection_confidence=0.7,
#     min_tracking_confidence=0.7
# )

# Video capture
cap = cv2.VideoCapture(0)

# Constants for smoothing
alpha = 0.75
prev_positions = [None] * 5

# Values for flickering control
visibility_score = [0] * 5

# Calculates fingernail points on a hand
# tip - fingernail landmark
# dip - joint before the tip
def get_nail(tip, dip):
    dx = tip.x - dip.x
    dy = tip.y - dip.y
    dz = tip.z - dip.z

    # Locate the nail bed on the finger
    nail_x = tip.x - dx * 0.2
    nail_y = tip.y - dy * 0.2

    # 2D rotation
    angle = math.atan2(dy, dx)

    # 3D tilt (for depth)
    tilt = math.atan2(dz, math.sqrt(dx*dx + dy*dy))

    return nail_x, nail_y, angle, tilt


def smooth_angle(prev, curr, alpha):
    diff = curr - prev
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return prev + diff * (1- alpha)


# Process video frames
while True:
    # Set the frame to read
    ret, frame = cap.read()
    if not ret:
        break

    # Mirror the frame
    frame = cv2.flip(frame, 1)

    # Store frame dimensions
    h, w, _ = frame.shape

    # Convert to RGB and give to Mediapipe for processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_rgb = mp.Image(image_format=ImageFormat.SRGB, data=rgb_frame)

    # Process hand detection results
    timestamp = int(time.time() * 1000)
    results = landmarker.detect_for_video(mp_rgb, timestamp)

    # Enter if a hand is detected facing down
    if results.hand_landmarks:
        # Store the first hand and its landmarks
        hand = results.hand_landmarks[0]

        wrist = hand[0]
        middle = hand[9]
        palm_facing_camera = wrist.z < middle.y

        # Fingertips and pre-tip joints
        tips = [4, 8, 12, 16, 20]  # Thumb to pinky
        dips = [3, 7, 11, 15, 19]

        for i in range(5):
            tip = hand[tips[i]]
            dip = hand[dips[i]]

            dz = tip.z - dip.z
            if palm_facing_camera:
                facing = dz < -0.01
            else:
                facing = dz < 0.02

            if facing:
                visibility_score[i] += 1
            else:
                visibility_score[i] -= 1

            visibility_score[i] = max(-3, min(3, visibility_score[i]))
            visible = visibility_score[i] > 0

            if not visible:
                prev_positions[i] = None
                continue

            # Get nail positions from the hand landmark
            nail_x, nail_y, angle, tilt = get_nail(tip, dip)

            # Scale according to depth
            scale = max(0.4, 1 - abs(tilt) * 3)

            # Apply smoothing
            if prev_positions[i] is not None:
                prev = prev_positions[i]
                nail_x = prev[0] * alpha + nail_x * (1 - alpha)
                nail_y = prev[1] * alpha + nail_y * (1 - alpha)
                angle = prev[2] * alpha + angle * (1 - alpha)
                tilt = prev[3] * alpha + tilt * (1 - alpha)
                scale = prev[4] * alpha + scale * (1 - alpha)

                # nail_x = smooth_angle(prev[0], nail_x, alpha)
                # nail_y = smooth_angle(prev[1], nail_y, alpha)
                # angle = smooth_angle(prev[2], angle, alpha)
                # tilt = smooth_angle(prev[3], tilt, alpha)
                # scale = smooth_angle(prev[4], scale, alpha)

            prev_positions[i] = (nail_x, nail_y, angle, tilt, scale)

            # Convert to pixels
            px = int(nail_x * w)
            py = int(nail_y * h)
            size_x = int(10 * scale)
            size_y = int(20 * scale)

            # cv2.circle(frame, (px, py), 5, (0, 255, 0), -1)

            # Draw red ellipse over nails
            cv2.ellipse(frame, (px, py), (size_x, size_y), math.degrees(angle), 0, 360, (0, 0, 255), -1)

    # Step 6: Display video
    cv2.imshow("AR Nails Test", frame)

    # Exit if user presses ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Step 7: Cleanup
cap.release()
cv2.destroyAllWindows()