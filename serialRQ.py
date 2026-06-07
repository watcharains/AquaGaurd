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


# --- Test / Debug ---
if __name__ == "__main__":
    # Simulate without hardware
    test_lines = [
        "$,350.5,1.2,7.1,28.5,#",
        "$,invalid,data,#",        # bad format
        "$,420.0,0.8,6.9,29.1,#",
    ]
    for line in test_lines:
        result = parse_data(line)
        print(f"Input : {line}")
        print(f"Output: {result}\n")