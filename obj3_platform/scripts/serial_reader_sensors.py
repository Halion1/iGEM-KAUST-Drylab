import serial, threading, json
from data_store import push_reading

SERIAL_PORT = "/dev/ttyUSB0"   # or "COM3" on Windows
BAUD_RATE   = 115200

def start_reader():
    def _loop():
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                try:
                    push_reading(json.loads(line))
                except json.JSONDecodeError:
                    pass
    t = threading.Thread(target=_loop, daemon=True)
    t.start()