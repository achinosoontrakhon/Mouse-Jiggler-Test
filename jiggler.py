#!/usr/bin/env python3
"""Mouse Jiggler - macOS menu bar app.

Moves the mouse in small, random, human-like motions at random intervals,
and can stop itself automatically after a chosen time.
"""
import math
import random
import threading
import time

import rumps
from Quartz import (
    CGEventCreate,
    CGEventCreateMouseEvent,
    CGEventGetLocation,
    CGEventPost,
    kCGEventMouseMoved,
    kCGHIDEventTap,
    kCGMouseButtonLeft,
)

IDLE_TITLE = "🖱"
ACTIVE_TITLE = "🖱●"

AUTO_STOP_OPTIONS = [("Never", 0), ("15 minutes", 15), ("30 minutes", 30),
                     ("1 hour", 60), ("2 hours", 120), ("4 hours", 240),
                     ("8 hours", 480)]
INTERVAL_OPTIONS = [("Frequent (5-15 s)", (5, 15)),
                    ("Normal (15-45 s)", (15, 45)),
                    ("Relaxed (45-120 s)", (45, 120))]
DISTANCE_OPTIONS = [("Small (5-30 px)", (5, 30)),
                    ("Medium (20-100 px)", (20, 100)),
                    ("Large (50-300 px)", (50, 300))]


def mouse_position():
    loc = CGEventGetLocation(CGEventCreate(None))
    return loc.x, loc.y


def move_to(x, y):
    ev = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (x, y), kCGMouseButtonLeft)
    CGEventPost(kCGHIDEventTap, ev)


def ease(t):
    """Smooth start/stop (ease-in-out)."""
    return 0.5 - 0.5 * math.cos(math.pi * t)


def human_move(dx, dy, duration):
    """Glide the cursor by (dx, dy) along a slightly curved, eased path."""
    sx, sy = mouse_position()
    steps = max(10, int(duration * 60))
    # Perpendicular bow gives the path a natural curve.
    bow = random.uniform(-0.15, 0.15)
    for i in range(1, steps + 1):
        t = ease(i / steps)
        curve = math.sin(math.pi * t) * bow
        x = sx + dx * t - dy * curve
        y = sy + dy * t + dx * curve
        move_to(x, y)
        time.sleep(duration / steps)


class Jiggler(rumps.App):
    def __init__(self):
        super().__init__("Mouse Jiggler", title=IDLE_TITLE, quit_button=None)
        self.running = False
        self.stop_event = threading.Event()
        self.thread = None
        self.deadline = None
        self.auto_stop_min = 0
        self.interval = INTERVAL_OPTIONS[1][1]
        self.distance = DISTANCE_OPTIONS[1][1]

        self.toggle_item = rumps.MenuItem("Start", callback=self.toggle)
        self.status_item = rumps.MenuItem("Stopped")
        self.status_item.set_callback(None)

        self.auto_menu = self._radio_menu("Auto-stop", AUTO_STOP_OPTIONS,
                                          self._set_auto_stop, 0)
        self.interval_menu = self._radio_menu("Interval", INTERVAL_OPTIONS,
                                              self._set_interval, 1)
        self.distance_menu = self._radio_menu("Distance", DISTANCE_OPTIONS,
                                              self._set_distance, 1)

        self.menu = [
            self.toggle_item,
            self.status_item,
            None,
            self.auto_menu,
            self.interval_menu,
            self.distance_menu,
            None,
            rumps.MenuItem("Quit", callback=self.quit_app),
        ]

        self.ticker = rumps.Timer(self._tick, 1)
        self.ticker.start()

    # ---- menu helpers -------------------------------------------------
    def _radio_menu(self, title, options, handler, default_idx):
        parent = rumps.MenuItem(title)
        for i, (label, value) in enumerate(options):
            item = rumps.MenuItem(label, callback=self._make_cb(parent, handler, value))
            item.state = 1 if i == default_idx else 0
            parent.add(item)
        return parent

    @staticmethod
    def _make_cb(parent, handler, value):
        def cb(sender):
            for item in parent.values():
                item.state = 0
            sender.state = 1
            handler(value)
        return cb

    def _set_auto_stop(self, minutes):
        self.auto_stop_min = minutes
        if self.running:
            self.deadline = time.time() + minutes * 60 if minutes else None

    def _set_interval(self, rng):
        self.interval = rng

    def _set_distance(self, rng):
        self.distance = rng

    # ---- start / stop -------------------------------------------------
    def toggle(self, _):
        self.stop() if self.running else self.start()

    def start(self):
        self.running = True
        self.stop_event.clear()
        self.deadline = time.time() + self.auto_stop_min * 60 if self.auto_stop_min else None
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        self.toggle_item.title = "Stop"
        self.title = ACTIVE_TITLE

    def stop(self):
        self.running = False
        self.stop_event.set()
        self.toggle_item.title = "Start"
        self.title = IDLE_TITLE
        self.status_item.title = "Stopped"

    def quit_app(self, _):
        self.stop_event.set()
        rumps.quit_application()

    # ---- worker -------------------------------------------------------
    def _loop(self):
        while not self.stop_event.is_set():
            wait = random.uniform(*self.interval)
            if self.stop_event.wait(wait):
                break
            self._jiggle()

    def _jiggle(self):
        dist = random.uniform(*self.distance)
        angle = random.uniform(0, 2 * math.pi)
        dx, dy = dist * math.cos(angle), dist * math.sin(angle)
        dur = random.uniform(0.25, 0.8)
        human_move(dx, dy, dur)
        # Often drift back so the cursor doesn't wander across the screen.
        if random.random() < 0.7 and not self.stop_event.is_set():
            time.sleep(random.uniform(0.2, 0.9))
            human_move(-dx, -dy, random.uniform(0.25, 0.8))

    # ---- UI tick (main thread) ---------------------------------------
    def _tick(self, _):
        if not self.running:
            return
        if self.deadline is None:
            self.status_item.title = "Running"
            return
        remaining = int(self.deadline - time.time())
        if remaining <= 0:
            self.stop()
            rumps.notification("Mouse Jiggler", "Stopped", "Auto-stop timer finished.")
            return
        h, rem = divmod(remaining, 3600)
        m, s = divmod(rem, 60)
        self.status_item.title = f"Running - stops in {h:d}:{m:02d}:{s:02d}"


if __name__ == "__main__":
    Jiggler().run()
