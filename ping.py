import asyncio
import aiohttp
import ctypes
from ctypes import Structure, byref, wintypes



class CONSOLE_SCREEN_BUFFER_INFO(Structure):
    _fields_ = [
        ("dwSize", wintypes._COORD),
        ("dwCursorPosition", wintypes._COORD),
        ("wAttributes", wintypes.WORD),
        ("srWindow", wintypes.SMALL_RECT),
        ("dwMaximumWindowSize", wintypes._COORD),
    ]

class Colors:
    LIGHT_GREEN = '\033[38;5;120m'
    DARK_RED = '\033[38;5;124m'
    RESET = '\033[0m'

def set_console_height(lines=45):
    """Устанавливает только высоту консольного окна (Windows 10/11)"""
    try:
        STD_OUTPUT_HANDLE = -11
        handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        
        buf_info = CONSOLE_SCREEN_BUFFER_INFO()
        ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, byref(buf_info))
        
        current_width = buf_info.srWindow.Right - buf_info.srWindow.Left + 1
        current_height = buf_info.srWindow.Bottom - buf_info.srWindow.Top + 1

        new_size = wintypes._COORD(buf_info.dwSize.X, lines)
        ctypes.windll.kernel32.SetConsoleScreenBufferSize(handle, new_size)
        
        new_rect = wintypes.SMALL_RECT(
            0,
            0,
            current_width - 1,
            lines - 1
        )
        ctypes.windll.kernel32.SetConsoleWindowInfo(handle, True, byref(new_rect))
    except Exception as e:
        print(f"Ошибка изменения размера окна: {e}")

class Colors:
    GREEN = '\033[92m'
    RED = '\033[31m'
    RESET = '\033[0m'

async def check_servers():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.arizona-five.com/launcher/servers") as resp:
            servers = (await resp.json())["arizona"]
        
        servers.append({"ip": "80.66.82.147", "name": "Vice City", "number": 1000})
        unique_servers = {s["ip"]: s for s in servers}.values()
        sorted_servers = sorted(unique_servers, key=lambda x: x["number"])
        
        print(f"Проверяем {len(sorted_servers)} серверов:")
        
        tasks = [asyncio.create_task(check_server(session, s)) for s in sorted_servers]
        results = await asyncio.gather(*tasks)
        
        print("=" * 63)
        for server, (status, color) in zip(sorted_servers, results):
            server_title = f"[{server['number']}]{server['name']}"
            print(f"{server_title:<16} {server['ip']:16} {color}{status}{Colors.RESET}")
        print("=" * 63)

async def check_server(session, server):
    try:
        async with session.get(f"http://{server['ip']}", timeout=3) as resp:
            if resp.status == 200:
                return ("√ Сервер успешно пропингован!", Colors.GREEN)
            return (f"× Ошибка http запроса: {resp.status}", Colors.RED)
    except Exception:
        return ("× Ошибка пропинговки!", Colors.RED)
        
def wait_for_any_key():
    print("Нажмите любую клавишу для выхода...", end='', flush=True)
    import msvcrt
    msvcrt.getch()
    print("\033[K", end='\r')

if __name__ == "__main__":
    set_console_height()
    ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    ctypes.windll.kernel32.SetConsoleCP(65001)
    asyncio.run(check_servers())
    wait_for_any_key()