#!/usr/bin/env python3
"""build_device.py - build the Live to TouchDesigner OSC Streamer Max for Live device (.amxd)."""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
M4L_COMMON = os.path.join(HERE, "..", "finishing-kit", "m4l")
if M4L_COMMON not in sys.path:
    sys.path.insert(0, M4L_COMMON)

import amxd

USER_LIBRARY_M4L = "/Volumes/Libraries/MY_MUSIC/_ABLETON/User Library/Presets/Audio Effects/Max Audio Effect"

def box(id_, maxclass, rect, **kw):
    b = {"id": id_, "maxclass": maxclass, "patching_rect": rect}
    b.update(kw)
    return {"box": b}

def newobj(id_, text, rect, inlets=1, outlets=1, outlettype=None, **kw):
    if outlettype is None:
        outlettype = [""]
    return box(id_, "newobj", rect, text=text, numinlets=inlets, numoutlets=outlets, outlettype=outlettype, **kw)

def message(id_, text, rect, inlets=2, outlets=1, **kw):
    return box(id_, "message", rect, text=text, numinlets=inlets, numoutlets=outlets, outlettype=[""], **kw)

def live_dial(id_, name, rect, pres, lo=0.0, hi=1.0, init=0.0, unitstyle=1):
    valueof = {
        "parameter_longname": name,
        "parameter_shortname": name,
        "parameter_type": 0,
        "parameter_mmin": lo,
        "parameter_mmax": hi,
        "parameter_initial": [init],
        "parameter_initial_enable": 1,
        "parameter_unitstyle": unitstyle
    }
    return box(id_, "live.dial", rect, numinlets=1, numoutlets=2, outlettype=["", "float"],
               parameter_enable=1, varname=name, presentation=1, presentation_rect=pres,
               saved_attribute_attributes={"valueof": valueof})

def comment(id_, text, rect, pres=None, fontsize=10.0, fontface=0):
    kw = {"fontsize": fontsize, "fontface": fontface}
    if pres:
        kw.update({"presentation": 1, "presentation_rect": pres})
    return box(id_, "comment", rect, text=text, numinlets=1, numoutlets=0, **kw)

def build_device():
    with open(os.path.join(M4L_COMMON, "spike_a_trim.json")) as f:
        p = json.load(f)

    pt = p["patcher"]
    pt["rect"] = [100.0, 100.0, 750.0, 600.0]
    pt["openrect"] = [0.0, 0.0, 230.0, 115.0]
    pt["devicewidth"] = 230.0
    pt["description"] = "Live to TouchDesigner OSC Streamer"

    boxes = [
        # Audio I/O Pass-through
        newobj("obj-1", "plugin~", [30.0, 30.0, 53.0, 20.0], inlets=2, outlets=2, outlettype=["signal", "signal"]),
        newobj("obj-2", "plugout~", [30.0, 480.0, 62.0, 20.0], inlets=2, outlets=0, outlettype=[]),
        
        # Sum to mono & scale by 0.5
        newobj("obj-3", "+~", [120.0, 70.0, 30.0, 20.0], inlets=2, outlets=1, outlettype=["signal"]),
        newobj("obj-4", "*~ 0.5", [120.0, 100.0, 45.0, 20.0], inlets=2, outlets=1, outlettype=["signal"]),

        # Gain Sensitivity
        live_dial("obj-5", "Sensitivity", [300.0, 30.0, 44.0, 48.0], pres=[8.0, 40.0, 44.0, 48.0], lo=0.1, hi=10.0, init=1.0, unitstyle=1),
        newobj("obj-6", "*~ 1.", [120.0, 140.0, 40.0, 20.0], inlets=2, outlets=1, outlettype=["signal"]),

        # RMS (Overall Energy)
        newobj("obj-7", "peakamp~ 20", [120.0, 180.0, 78.0, 20.0], inlets=1, outlets=1, outlettype=["float"]),
        message("obj-8", "/live/rms $1", [120.0, 210.0, 80.0, 20.0]),

        # Low Band Filter & Amp
        newobj("obj-9", "lores~ 250 0.8", [220.0, 180.0, 85.0, 20.0], inlets=3, outlets=1, outlettype=["signal"]),
        newobj("obj-10", "peakamp~ 20", [220.0, 210.0, 78.0, 20.0], inlets=1, outlets=1, outlettype=["float"]),
        message("obj-11", "/live/low $1", [220.0, 240.0, 78.0, 20.0]),

        # High Band Filter & Amp (Highs / Transients around 4.5 kHz)
        newobj("obj-12", "reson~ 1. 4500 1.5", [320.0, 180.0, 95.0, 20.0], inlets=4, outlets=1, outlettype=["signal"]),
        newobj("obj-13", "peakamp~ 20", [320.0, 210.0, 78.0, 20.0], inlets=1, outlets=1, outlettype=["float"]),
        message("obj-14", "/live/high $1", [320.0, 240.0, 82.0, 20.0]),

        # Mid Band Filter & Amp
        newobj("obj-15", "reson~ 1. 1000 2.", [420.0, 180.0, 95.0, 20.0], inlets=4, outlets=1, outlettype=["signal"]),
        newobj("obj-16", "peakamp~ 20", [420.0, 210.0, 78.0, 20.0], inlets=1, outlets=1, outlettype=["float"]),
        message("obj-17", "/live/mid $1", [420.0, 240.0, 78.0, 20.0]),

        # Performance Macros
        live_dial("obj-18", "Morph", [550.0, 30.0, 44.0, 48.0], pres=[60.0, 40.0, 40.0, 48.0], lo=0.0, hi=1.0, init=0.0),
        message("obj-19", "/live/macro1 $1", [550.0, 90.0, 95.0, 20.0]),

        live_dial("obj-20", "Speed", [600.0, 30.0, 44.0, 48.0], pres=[102.0, 40.0, 40.0, 48.0], lo=0.0, hi=1.0, init=0.5),
        message("obj-21", "/live/macro2 $1", [600.0, 90.0, 95.0, 20.0]),

        live_dial("obj-22", "Decay", [650.0, 30.0, 44.0, 48.0], pres=[144.0, 40.0, 40.0, 48.0], lo=0.0, hi=1.0, init=0.5),
        message("obj-23", "/live/macro3 $1", [650.0, 90.0, 95.0, 20.0]),

        live_dial("obj-24", "Color", [700.0, 30.0, 44.0, 48.0], pres=[186.0, 40.0, 40.0, 48.0], lo=0.0, hi=1.0, init=0.0),
        message("obj-25", "/live/macro4 $1", [700.0, 90.0, 95.0, 20.0]),

        # UDP Send (:7000)
        newobj("obj-26", "udpsend 127.0.0.1 7000", [250.0, 380.0, 130.0, 20.0], inlets=1, outlets=0, outlettype=[]),

        # Presentation UI Headers
        comment("obj-27", "TD STREAMER", [30.0, 520.0, 120.0, 20.0], pres=[8.0, 8.0, 120.0, 18.0], fontsize=11.0, fontface=1),
        comment("obj-28", "OSC 127.0.0.1:7000", [30.0, 545.0, 120.0, 20.0], pres=[8.0, 24.0, 140.0, 14.0], fontsize=9.0)
    ]
    pt["boxes"] = boxes

    cords = [
        # Pass audio straight through
        (["obj-1", 0], ["obj-2", 0]),
        (["obj-1", 1], ["obj-2", 1]),

        # Sum to mono
        (["obj-1", 0], ["obj-3", 0]),
        (["obj-1", 1], ["obj-3", 1]),
        (["obj-3", 0], ["obj-4", 0]),

        # Gain scaling
        (["obj-4", 0], ["obj-6", 0]),
        (["obj-5", 0], ["obj-6", 1]),

        # RMS
        (["obj-6", 0], ["obj-7", 0]),
        (["obj-7", 0], ["obj-8", 0]),
        (["obj-8", 0], ["obj-26", 0]),

        # Low
        (["obj-6", 0], ["obj-9", 0]),
        (["obj-9", 0], ["obj-10", 0]),
        (["obj-10", 0], ["obj-11", 0]),
        (["obj-11", 0], ["obj-26", 0]),

        # High
        (["obj-6", 0], ["obj-12", 0]),
        (["obj-12", 0], ["obj-13", 0]),
        (["obj-13", 0], ["obj-14", 0]),
        (["obj-14", 0], ["obj-26", 0]),

        # Mid
        (["obj-6", 0], ["obj-15", 0]),
        (["obj-15", 0], ["obj-16", 0]),
        (["obj-16", 0], ["obj-17", 0]),
        (["obj-17", 0], ["obj-26", 0]),

        # Macros
        (["obj-18", 0], ["obj-19", 0]),
        (["obj-19", 0], ["obj-26", 0]),

        (["obj-20", 0], ["obj-21", 0]),
        (["obj-21", 0], ["obj-26", 0]),

        (["obj-22", 0], ["obj-23", 0]),
        (["obj-23", 0], ["obj-26", 0]),

        (["obj-24", 0], ["obj-25", 0]),
        (["obj-25", 0], ["obj-26", 0]),
    ]
    pt["lines"] = [{"patchline": {"source": s, "destination": d}} for s, d in cords]

    param_names = ["Sensitivity", "Morph", "Speed", "Decay", "Color"]
    pt["parameters"] = {
        "obj-5": ["Sensitivity", "Sens", 0],
        "obj-18": ["Morph", "Morph", 0],
        "obj-20": ["Speed", "Speed", 0],
        "obj-22": ["Decay", "Decay", 0],
        "obj-24": ["Color", "Color", 0],
        "parameterbanks": {
            "0": {
                "index": 0,
                "name": "",
                "parameters": param_names
            }
        }
    }
    return p

def main():
    dev = build_device()
    data = amxd.build(dev, kind="audio")

    local_out = os.path.join(HERE, "TouchDesigner_Streamer.amxd")
    with open(local_out, "wb") as f:
        f.write(data)
    print(f"wrote {local_out} ({len(data)} bytes)")

    if os.path.isdir(USER_LIBRARY_M4L):
        user_out = os.path.join(USER_LIBRARY_M4L, "TouchDesigner_Streamer.amxd")
        with open(user_out, "wb") as f:
            f.write(data)
        print(f"wrote {user_out}")

if __name__ == "__main__":
    main()
