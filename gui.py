import tkinter as tk
import serial
import threading

def parse_data(line: str) -> dict | None:
    line = line.strip()
    if not (line.startswith('$') and line.endswith('#')):
        return None
    parts = line.split(',')
    if len(parts) != 6:
        return None
    try:
        return {
            "tds":       float(parts[1]),
            "turbidity": float(parts[2]),
            "ph":        float(parts[3]),
            "temp":      float(parts[4])
        }
    except ValueError:
        return None


class WaterQualityGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Water Quality Monitor")
        self.root.geometry("500x350")
        self.root.configure(bg="#1e1e2e")
        self.running = False
        self.ser = None

        self._build_ui()

    def _build_ui(self):
        # --- Title ---
        tk.Label(self.root, text="💧 Water Quality Monitor",
                 bg="#1e1e2e", fg="#cdd6f4",
                 font=("Arial", 16, "bold")).pack(pady=10)

        # --- Sensor Cards ---
        card_frame = tk.Frame(self.root, bg="#1e1e2e")
        card_frame.pack(pady=10)

        self.labels = {}
        sensors = [
            ("TDS",       "ppm", "#89b4fa"),
            ("Turbidity", "NTU", "#fab387"),
            ("pH",        "",    "#a6e3a1"),
            ("Temp",      "°C",  "#f38ba8"),
        ]

        for col, (name, unit, color) in enumerate(sensors):
            frame = tk.Frame(card_frame, bg="#313244",
                             padx=20, pady=15, relief=tk.RAISED, bd=2)
            frame.grid(row=0, column=col, padx=8)

            tk.Label(frame, text=name, bg="#313244",
                     fg="#cdd6f4", font=("Arial", 10)).pack()

            lbl = tk.Label(frame, text="--", bg="#313244",
                           fg=color, font=("Arial", 22, "bold"))
            lbl.pack()

            tk.Label(frame, text=unit, bg="#313244",
                     fg="#a6adc8", font=("Arial", 9)).pack()

            self.labels[name.lower()] = lbl

        # --- Port Config ---
        config_frame = tk.Frame(self.root, bg="#1e1e2e")
        config_frame.pack(pady=10)

        tk.Label(config_frame, text="Port:", bg="#1e1e2e",
                 fg="#cdd6f4").grid(row=0, column=0, padx=5)

        self.port_entry = tk.Entry(config_frame, width=8)
        self.port_entry.insert(0, "COM3")
        self.port_entry.grid(row=0, column=1, padx=5)

        tk.Label(config_frame, text="Baud:", bg="#1e1e2e",
                 fg="#cdd6f4").grid(row=0, column=2, padx=5)

        self.baud_entry = tk.Entry(config_frame, width=8)
        self.baud_entry.insert(0, "115200")
        self.baud_entry.grid(row=0, column=3, padx=5)

        # --- Buttons ---
        btn_frame = tk.Frame(self.root, bg="#1e1e2e")
        btn_frame.pack(pady=5)

        self.start_btn = tk.Button(btn_frame, text="▶ Start",
                                   bg="#a6e3a1", fg="#1e1e2e",
                                   font=("Arial", 10, "bold"),
                                   command=self.start_reading, width=10)
        self.start_btn.grid(row=0, column=0, padx=8)

        self.stop_btn = tk.Button(btn_frame, text="■ Stop",
                                  bg="#f38ba8", fg="#1e1e2e",
                                  font=("Arial", 10, "bold"),
                                  command=self.stop_reading,
                                  width=10, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=8)

        # --- Status Bar ---
        self.status = tk.Label(self.root, text="Status: Disconnected",
                               bg="#181825", fg="yellow",
                               font=("Arial", 9), anchor="w")
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def start_reading(self):
        port = self.port_entry.get()
        baud = int(self.baud_entry.get())
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
            self.running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status.config(text=f"Status: Connected to {port}", fg="green")
            threading.Thread(target=self._read_loop, daemon=True).start()
        except serial.SerialException as e:
            self.status.config(text=f"Error: {e}", fg="red")

    def stop_reading(self):
        self.running = False
        if self.ser:
            self.ser.close()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status.config(text="Status: Disconnected", fg="yellow")

    def _read_loop(self):
        while self.running:
            try:
                raw  = self.ser.readline().decode('utf-8').strip()
                data = parse_data(raw)
                if data:
                    self.root.after(0, self._update_labels, data)
            except (UnicodeDecodeError, serial.SerialException):
                pass

    def _update_labels(self, data):
        self.labels["tds"].config(text=f"{data['tds']:.1f}")
        self.labels["turbidity"].config(text=f"{data['turbidity']:.1f}")
        self.labels["ph"].config(text=f"{data['ph']:.1f}")
        self.labels["temp"].config(text=f"{data['temp']:.1f}")
        self.status.config(text=f"Status: Live | "
                                f"TDS={data['tds']} | "
                                f"Turb={data['turbidity']} | "
                                f"pH={data['ph']} | "
                                f"Temp={data['temp']}",
                           fg="green")

    def on_close(self):
        self.stop_reading()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app  = WaterQualityGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()