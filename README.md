# Live to TouchDesigner OSC Streamer 🌌🎛️

A real-time audio analysis and visual performance bridge between **Ableton Live** and **TouchDesigner**.

Extracts multi-band spectral dynamics, overall RMS volume, and 4 performance macro controls from any audio track in Live and streams them over ultra-low-latency OSC to drive generative 3D visuals, reactive shaders, and interactive skies in TouchDesigner.

---

## Architecture Overview

```
 [ Ableton Live Audio Track / Master ]
                 │
                 ▼
 [ TouchDesigner_Streamer.amxd (Audio Effect) ]
      ├── Audio Pass-Through ──► (Track Output / Master)
      │
      ├── Spectral & Dynamic Feature Extraction:
      │     • Full RMS Amplitude (peakamp~ 20ms)
      │     • Low Band / Bass (lores~ 250 Hz)
      │     • Mid Band (reson~ 1000 Hz)
      │     • High Band / Transients (reson~ 4500 Hz)
      │
      └── 4 Performance Macro Knobs (Morph, Speed, Decay, Color)
                 │
                 │ UDP OSC Stream (127.0.0.1:7000)
                 ▼
 [ TouchDesigner (OSC In CHOP) ] ──► (Particle Systems / Sky Shaders / Lights)
```

---

## Features

- **True Audio Pass-Through**: Clean `plugin~` to `plugout~` stereo routing with zero coloration or latency added to your audio path.
- **Sensitivity Knob**: Master input gain multiplier (`0.1x` to `10.0x`) to calibrate audio dynamics for quiet atmospheric signals or loud master drops without clipping the audio track.
- **Multi-Band Audio Extraction**:
  - **RMS**: Overall signal energy, ideal for global scale, light intensity, or camera shake.
  - **Low (Sub/Bass)**: Filtered around 250 Hz, perfect for kick/bass drum pulses and particle explosions.
  - **Mid (Vocals/Melody)**: Filtered around 1000 Hz, responsive to chord progressions, leads, and snares.
  - **High (Air/Transients)**: Filtered around 4500 Hz, captures hi-hats, percussive clicks, and vocal sibilance.
- **4 Real-Time Performance Macro Dials**:
  - **Morph (`/live/macro1`)**: 0.0 to 1.0
  - **Speed (`/live/macro2`)**: 0.0 to 1.0
  - **Decay (`/live/macro3`)**: 0.0 to 1.0
  - **Color (`/live/macro4`)**: 0.0 to 1.0
  *(All 4 macros can be automated in Live clips or mapped to physical MIDI controllers!)*

---

## Quick Start Guide

### 1. Load the Device in Ableton Live
1. Open Ableton Live.
2. In the Live Browser, navigate to:
   ```text
   User Library ──► Presets ──► Audio Effects ──► Max Audio Effect ──► TouchDesigner_Streamer.amxd
   ```
3. Drag **`TouchDesigner_Streamer.amxd`** onto:
   - Your **Master Track** (for full-mix reactive visuals), or
   - Specific stems/submixes (e.g., Drums, Synths, Bass).

### 2. Configure TouchDesigner
1. Open your TouchDesigner project (e.g. generative sky, particle system, or terrain).
2. Press `Tab` and create an **OSC In CHOP**.
3. In the parameter dialog of the **OSC In CHOP**:
   - **Network Port**: `7000`
   - **Active**: `On`
4. In TouchDesigner, you will immediately see channels appear:
   - `live/rms`
   - `live/low`
   - `live/mid`
   - `live/high`
   - `live/macro1`
   - `live/macro2`
   - `live/macro3`
   - `live/macro4`

### 3. Smooth & Map in TouchDesigner
In TouchDesigner, pipe the **OSC In CHOP** through:
- A **Lag CHOP** or **Filter CHOP** for smooth, organic visual motion.
- A **Math CHOP** to rescale channels to desired rotation, scale, color, or camera coordinates.

---

## OSC Channel Reference

| OSC Address | Data Type | Range | Description |
| :--- | :--- | :--- | :--- |
| `/live/rms` | Float | `0.0 – 1.0` | Overall RMS amplitude energy |
| `/live/low` | Float | `0.0 – 1.0` | Bass & Kick energy (< 250 Hz) |
| `/live/mid` | Float | `0.0 – 1.0` | Midrange & chord energy (~ 1000 Hz) |
| `/live/high` | Float | `0.0 – 1.0` | Transients & Hi-Hats (~ 4500 Hz) |
| `/live/macro1` | Float | `0.0 – 1.0` | Macro 1 (`Morph`) |
| `/live/macro2` | Float | `0.0 – 1.0` | Macro 2 (`Speed`) |
| `/live/macro3` | Float | `0.0 – 1.0` | Macro 3 (`Decay`) |
| `/live/macro4` | Float | `0.0 – 1.0` | Macro 4 (`Color`) |

---

## Technical Specifications

| Parameter | Value |
| :--- | :--- |
| **Protocol** | UDP OSC |
| **Host** | `127.0.0.1` (Localhost) |
| **Port** | `7000` |
| **Audio Rate** | Native Live sample rate (44.1 / 48 / 96 kHz) |
| **Analysis Update Interval** | 20 ms (~50 Hz visual frame rate) |
| **Rebuild Command** | `python3 build_device.py` |
| **Target AMXD** | Standalone native Max Audio Effect (`.amxd`) |
