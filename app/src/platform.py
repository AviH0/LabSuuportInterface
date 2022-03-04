

import sys

if sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
    # Windows
    UPDATER_URL = 'https://github.com/AviH0/LabSupportInterface/releases/download/Latest/Updater_Windows.exe'
    UPDATER_FILE = 'Update.exe'
    MAIN_EXE_NAME = "LabSupportClient.exe"
    DEFAULT_URL = "https://github.com/AviH0/LabSupportInterface/releases/download/Latest/LS_Windows.zip"

else:
    # Linux or other:
    UPDATER_URL = 'https://github.com/AviH0/LabSupportInterface/releases/download/Latest/Updater_Linux'
    UPDATER_FILE = 'Update'
    MAIN_EXE_NAME = "LabSupportClient"
    DEFAULT_URL = "https://github.com/AviH0/LabSupportInterface/releases/download/Latest/LS_Linux.zip"