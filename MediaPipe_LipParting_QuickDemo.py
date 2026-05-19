"""Lip-parting detector demo for silent speech miming — shows GUI message when lips open. (OpenCV mediapipe based)"""

# =================================================================================================
# Master Parameters (change feely)
# =================================================================================================
# --- define default threshold (will be adjustable live in GUI via slider) ---
LIP_OPEN_THRESHOLD = 0.004  # normalised y-distance; -->  use slider to tune live
    # NOTE: the best thresh value already differs quite a bit between mike and I (beard?) 
    # so this might have to be finetuned to the subject before every session (very quick)

# --- Landmarkpoints used for parting calculation ---
UPPER_LIP_IDX      = 13     # upper inner lip landmark
LOWER_LIP_IDX      = 14     # lower inner lip landmark
    # NOTE: see here for full list of idxs: 
    # https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png

# --- GUI overlays ---
LIP_COLOR          = (255, 255, 255)  # BGR color for lip outline darwing on GUI
    # NOTE: (opencv only accepts BRG not RGB, mediapipe only RGB.. annoying but easy conversion - see below)
LIP_THICKNESS      = 1      # line thickness in pixels for lip outline darwing on GUI
FLAGMESSAGE        = 'MIMING' # 'BAAM!' # Message that is displayed on the GUI when lips are parted

# --- CSV export ---
EXPORT_CSV         = True                   # toggle event export on/off
CSV_FILENAME       = "lipparty_events.csv"  # output file (saved in current directory)
# =================================================================================================


# SCRIPT
# =================================================================================================
# SETUP CHECK AND PREP (change with caution)
# =================================================================================================
# --- Install dependencies ---
import subprocess, urllib.request, os, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "mediapipe", "opencv-python"])

# --- Download the pretrained face landmark mapping model from google (once) ---
MODEL = "face_landmarker.task"
if not os.path.exists(MODEL):
    print("Downloading model…")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
        MODEL)

# --- Imports / Aliases / Paths ---
import cv2, time, csv, mediapipe as mp
from mediapipe.tasks.python.vision.drawing_utils import DrawingSpec

Connections = mp.tasks.vision.FaceLandmarksConnections # list of pairs to form lipline instead of singular dots 
# NOTE: this is only relevant for drawing. the lip-parting value is derived from the 2 landmarkpoints 
draw = mp.tasks.vision.drawing_utils.draw_landmarks
lip_style = DrawingSpec(color=LIP_COLOR, thickness=LIP_THICKNESS)

# --- Create face landmarker --- 
landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(
    mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=MODEL),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_faces=1))

# ---Set up webcam & GUI ---
webcam = cv2.VideoCapture(0)
ts = 0

WIN = "Lip Detector | Q to quit"
cv2.namedWindow(WIN)
cv2.createTrackbar("Threshold x1000", WIN, int(LIP_OPEN_THRESHOLD * 1000), 50, lambda x: None)

# --- Event tracking state ---
t0 = time.time()          # wall-clock reference (seconds)
miming = False             # are lips currently parted?
event_start = 0.0          # start time of current event
events = []                # list of (event#, start_s, end_s, duration_s)


# =================================================================================================
# MAIN LOOP (change with caution)
# =================================================================================================
while webcam.isOpened():
    ok, frame = webcam.read()
    if not ok: break

    now = time.time() - t0  # seconds since script start

    # --- Detect landmarks ---
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # BRG to RGB conversion for mediapipe
    result = landmarker.detect_for_video(
        mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), ts)
    ts += 33

    thresh = cv2.getTrackbarPos("Threshold x1000", WIN) / 1000.0

    lips_open = False
    if result.face_landmarks:
        lm = result.face_landmarks[0]

        # --- Draw lip outline ---
        draw(frame, lm, Connections.FACE_LANDMARKS_LIPS, None, lip_style)

        # --- Measure lip gap & show flag ---
        gap = abs(lm[UPPER_LIP_IDX].y - lm[LOWER_LIP_IDX].y)
        cv2.putText(frame, f"gap: {gap:.4f}  thresh: {thresh:.4f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        lips_open = gap > thresh
        if lips_open:
            cv2.putText(frame, FLAGMESSAGE, (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

    # --- Track miming events ---
    if lips_open and not miming:
        miming = True
        event_start = now
    elif not lips_open and miming:
        miming = False
        events.append((len(events) + 1, round(event_start, 3),
                        round(now, 3), round(now - event_start, 3)))

    # --- Show event count ---
    cv2.putText(frame, f"events: {len(events)}", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

    cv2.imshow(WIN, frame)
    if cv2.waitKey(5) & 0xFF == ord("q"): break

# NOTE: probably not necessary, but if ongoing events (lipparting) while quitting should be preserved uncomment this. 
# Else just delete this block, then ongoing events while quitting will not be written into the output csv
# --- Close final event if still miming when quitting ---
# if miming:
#     now = time.time() - t0
#     events.append((len(events) + 1, round(event_start, 3),
#                     round(now, 3), round(now - event_start, 3)))



# =================================================================================================
# CLEANUP AND EXPORT (change with caution)
# =================================================================================================
# --- Export CSV ---
if EXPORT_CSV and events:
    with open(CSV_FILENAME, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["event", "start_s", "end_s", "duration_s"])
        w.writerows(events)
    print(f"Exported {len(events)} events to {CSV_FILENAME}")
elif EXPORT_CSV:
    print("No miming events detected — CSV not written.")

# --- Cleanup ---
landmarker.close(); webcam.release(); cv2.destroyAllWindows()

# DONE - WhoopWhoop 
