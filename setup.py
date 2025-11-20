from setuptools import setup

APP = ['owl_track.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False, 
    'iconfile': 'owltrack.icns',
    'plist': {
        'LSUIElement': True, 
        'CFBundleName': "OwlTrack",
        'CFBundleDisplayName': "OwlTrack",
        'CFBundleIdentifier': "com.lemondyai.owltrack",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHighResolutionCapable': True,
        # 网络权限（允许外部网络连接）
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True
        },
    },
    # 修正：只保留第三方库。不要放 os, json, time, threading 等内置库！
    'packages': ['rumps', 'requests', 'idna', 'urllib3', 'certifi', 'charset_normalizer'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)