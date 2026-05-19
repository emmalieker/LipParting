# Lip-Parting Detector (for Silent speech etc.)

Real-time lip-parting detection using MediaPipe face landmarks and OpenCV. Creates a GUI with realtime lip detection and live-threshold control via slider. Writes out a .csv with timestamped parting events. Built for detecting silent speech miming via webcam.

## How it works

The script tracks two inner-lip landmarks (indices 13 & 14) from MediaPipe's face landmarker and computes the normalised vertical gap between them. When the gap exceeds a threshold, a "MIMING" flag is shown on-screen. Events (start, end, duration) are logged and exported to CSV.

The threshold is adjustable live via a GUI slider — useful because the optimal value varies between subjects (e.g., facial hair and camera angle affect it).

## Demo

**GUI with live threshold slider and gap readout:**

![Slider GUI](Demo/Demo_Screenshot_00_Slider.png)

**Lip landmark overlay — lips closed (below threshold):**

![Lips closed - closeup](Demo/Demo_Screenshot_03_noPart.png)
![Lips closed - GUI](Demo/Demo_Screenshot_02_noPart.png)

**Lips parted — detection triggered:**

![Lips parted - closeup](Demo/Demo_Screenshot_03_Part.png)
![MIMING flag](Demo/Demo_Screenshot_04_Part.png)

## Quick start

```bash
python MediaPipe_LipParting_QuickDemo.py
```

Dependencies (`mediapipe`, `opencv-python`) and the face landmark model are downloaded automatically on first run. Press **Q** to quit the GUI.

## Configuration

All tuneable parameters are at the top of the script in the "Master":

| Parameter | Default | Description |
|---|---|---|
| `LIP_OPEN_THRESHOLD` | 0.004 | Starting threshold (adjustable live via slider) |
| `EXPORT_CSV` | True | Toggle CSV event export |
| `CSV_FILENAME` | `lipparty_events.csv` | Output filename |
| `FLAGMESSAGE` | `MIMING` | On-screen alert text |
