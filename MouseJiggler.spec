# PyInstaller spec: builds MouseJiggler.app (menu bar only, no Dock icon)
from PyInstaller.utils.hooks import collect_all, collect_submodules

datas, binaries, hidden = [], [], []
for pkg in ('rumps', 'objc', 'Foundation', 'AppKit', 'Quartz', 'CoreFoundation', 'PyObjCTools'):
    d, b, h = collect_all(pkg)
    datas += d; binaries += b; hidden += h
hidden += collect_submodules('Quartz')

a = Analysis(['jiggler.py'], datas=datas, binaries=binaries, hiddenimports=hidden)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='MouseJiggler', console=False)
coll = COLLECT(exe, a.binaries, a.datas, name='MouseJiggler')
app = BUNDLE(coll, name='MouseJiggler.app', bundle_identifier='com.example.mousejiggler',
             info_plist={'LSUIElement': True, 'CFBundleName': 'Mouse Jiggler'})
