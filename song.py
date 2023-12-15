from pynput import keyboard
import time

last_time = time.perf_counter()
deltas = []

def on_press(key):
    if key == keyboard.Key.esc:
        return False  # stop listener
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys
    if k in ['space']:  # keys of interest
        global last_time
        delta = time.perf_counter() - last_time
        last_time = time.perf_counter()
        print(delta)
        deltas.append(delta)

listener = keyboard.Listener(on_press=on_press)
listener.start()  # start to listen on a separate thread
listener.join()  # remove if main thread is polling self.keys

print(deltas)