import serial

def parse_data(line: str) -> dict | None:
    """Parse ESP32 serial format: $,tds,turbidity,ph,temp,#"""
    try:
        line = line.strip()
        if not (line.startswith('$') and line.endswith('#')):
            return None
        
        parts = line.split(',')
        # Expected: ['$', tds, turbidity, ph, temp, '#']
        if len(parts) != 6:
            return None
        
        return {
            "tds":       float(parts[1]),
            "turbidity": float(parts[2]),
            "ph":        float(parts[3]),
            "temp":      float(parts[4])
        }
    except (ValueError, IndexError):
        return None


class SerialReader:
    def __init__(self, port='COM20', baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=1)

    def read_data(self) -> dict | None:
        try:
            line = self.ser.readline().decode('utf-8').strip()
            if line:
                return parse_data(line)
        except (UnicodeDecodeError, serial.SerialException):
            return None

    def close(self):
        self.ser.close()
def main():
    ser = serial.Serial(
        port      = 'COM20',  # Windows: 'COM3'
        baudrate  = 115200,
        timeout   = 1
    )
    print("Listening on serial port...")

    while True:
        try:
            raw  = ser.readline().decode('utf-8').strip()
            data = parse_data(raw)

            if data:
                print(f"TDS: {data['tds']} ppm | "
                      f"Turbidity: {data['turbidity']} NTU | "
                      f"pH: {data['ph']} | "
                      f"Temp: {data['temp']} °C")
            else:
                print(f"Invalid data: {raw}")

        except KeyboardInterrupt:
            print("Stopped.")
            break
        except UnicodeDecodeError:
            print("Decode error, skipping line.")

    ser.close()

# --- Test / Debug ---
if __name__ == "__main__":
    main()