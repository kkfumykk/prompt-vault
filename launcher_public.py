import os
import socket
import sys
import time
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8080
URL = f"http://{HOST}:{PORT}"

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")


def is_port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def open_browser():
    time.sleep(1.2)
    webbrowser.open(URL)


def main():
    os.chdir(BASE_DIR)

    if is_port_in_use(HOST, PORT):
        print(f"[INFO] Prompt Vault Public サーバーは既に起動しています: {URL}")
        webbrowser.open(URL)
        return

    print("===================================================")
    print("      AI Prompt & Art Gallery (Public Edition)")
    print("===================================================")
    print(f"[INFO] サーバー起動中: {URL}")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    try:
        import uvicorn
        from app.main import app
        uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
    except Exception as e:
        print(f"[ERROR] 起動エラー: {e}")
        input("Enterキーを押して終了してください...")


if __name__ == "__main__":
    main()
