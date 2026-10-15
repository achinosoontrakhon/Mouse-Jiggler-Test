# PyInstaller spec: builds MouseJiggler.app (menu bar only, no Dock icon)
a = Analysis(['jiggler.py'], hiddenimports=['rumps', 'Quartz'])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='MouseJiggler', console=False)
coll = COLLECT(exe, a.binaries, a.datas, name='MouseJiggler')
app = BUNDLE(coll, name='MouseJiggler.app', bundle_identifier='com.example.mousejiggler',
             info_plist={'LSUIElement': True, 'CFBundleName': 'Mouse Jiggler'})
