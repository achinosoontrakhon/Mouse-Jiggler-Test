# Mouse Jiggler (macOS menu bar)

Menu bar app that moves the cursor in small, random, human-like motions.

## Run
```bash
pip3 install rumps pyobjc-framework-Quartz
python3 jiggler.py
```
Click the 🖱 icon in the menu bar → **Start**. The icon shows 🖱● while active.

On first run macOS will ask for permission: System Settings → Privacy & Security →
**Accessibility** → enable your Terminal (or the built app).

## Options (menu bar)
- **Auto-stop**: Never / 15m / 30m / 1h / 2h / 4h / 8h (with countdown)
- **Interval**: how often it moves (random within the range)
- **Distance**: how far it moves

## Build a standalone .app (optional)
```bash
pip3 install py2app
python3 setup.py py2app
```
The app appears in `dist/`. `LSUIElement` hides the Dock icon.
