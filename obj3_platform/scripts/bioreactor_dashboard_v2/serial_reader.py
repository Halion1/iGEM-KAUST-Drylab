import threading, time, math, random
from data_store import push_reading

def start_reader():
    def _loop():
        t = 0
        while True:
            push_reading({
                "temp":     round(37.0 + math.sin(t * 0.1) * 0.5 + random.uniform(-0.1, 0.1), 2),
                "ph":       round(7.0  + math.sin(t * 0.07) * 0.2 + random.uniform(-0.05, 0.05), 3),
                "pressure": round(1.01 + random.uniform(-0.01, 0.01), 3),
                "co2":      round(410  + math.sin(t * 0.05) * 20 + random.uniform(-5, 5), 1),
            })
            t += 1
            time.sleep(1.5)

    threading.Thread(target=_loop, daemon=True).start()