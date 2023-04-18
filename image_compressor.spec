# image_compressor.spec

block_cipher = None

added_files = [
    # Add any additional data files required by the script here, e.g.:
    # ('path/to/datafile.ext', 'destination/folder'),
]

a = Analysis(['ImageCompressorApp\main.py'],
             pathex=['C:\\Users\\arnau\\OneDrive\\Images\\Documents\\image processing application project\\git\\ImageCompressorApp\\ImageCompressorApp'],
             binaries=[],
             datas=added_files,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ImageCompressorApp',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon=None)
