import serial
import time

# demo to demonstrate closing the vice and then opening it

dio_port = '/dev/ttyACM0'
with serial.Serial(dio_port) as mcu:
    def terminal_command(command: str):
        print(f"Running command: {command}")
        mcu.write(command.encode())
        time.sleep(0.005)
        res = mcu.read(mcu.in_waiting).decode()
        print(f"res: '{res}'")
        time.sleep(0.005)
        parts = res.split("\n")
        print(parts)
        if len(parts) > 1:
            res = parts[1].strip("\r")
        return res

    time.sleep(5)
    # Close the vice by sending true to pin 0, which sets the pin to 0V
    res = terminal_command("dio set DO_G0 0 true\n")
    print(res)
    time.sleep(1)
    res = terminal_command("dio get DO_G0 output 0\n")
    print(res)
    time.sleep(1)

    # Open the vice by sending false to pin 0, which sets the pin to 24V
    res = terminal_command("dio set DO_G0 0 false\n")
    print(res)
    time.sleep(1)
    res = terminal_command("dio get DO_G0 output 0\n")
    print(res)

