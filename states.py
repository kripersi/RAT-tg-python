from aiogram.filters.state import State, StatesGroup


class MoveMouseCoord(StatesGroup):
    waiting_for_coords = State()


class MoveMouseDirection(StatesGroup):
    waiting_for_direction = State()
    waiting_for_offset = State()


class MsgBox(StatesGroup):
    waiting_for_text = State()


class MessageWrite(StatesGroup):
    waiting_for_text = State()


class CmdExec(StatesGroup):
    waiting_for_command = State()


class PythonExec(StatesGroup):
    waiting_for_code = State()


class ClipboardSet(StatesGroup):
    waiting_for_text = State()


class MicRecord(StatesGroup):
    waiting_for_seconds = State()


class KillProcess(StatesGroup):
    waiting_for_pid = State()


class VideoPc(StatesGroup):
    waiting_for_seconds = State()


class Download(StatesGroup):
    waiting_for_path = State()


class Run(StatesGroup):
    waiting_for_path = State()


class Wallpaper(StatesGroup):
    waiting_for_path = State()


class Ls(StatesGroup):
    waiting_for_path = State()


class OpenBrowser(StatesGroup):
    waiting_for_url = State()


class CreateMoreFolders(StatesGroup):
    waiting_for_count = State()
    waiting_for_name = State()
    waiting_for_text = State()


class DownloadFile(StatesGroup):
    waiting_for_file = State()


class WebcamRecord(StatesGroup):
    waiting_for_seconds = State()


class ClickImage(StatesGroup):
    waiting_for_photo = State()


