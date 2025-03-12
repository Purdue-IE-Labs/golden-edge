import pathlib
import gedge

import serial
import time

def open_vice_command(group: int = 0, pin: int = 0) -> str:
    command = f"dio set DO_G{group} {pin} false\n"
    return command

def close_vice_command(group: int = 0, pin: int = 0) -> str:
    command = f"dio set DO_G{group} {pin} true\n"
    return command

def read_vice_state_command(group: int = 0, pin: int = 0) -> str:
    command = f"dio get DO_G{group} output {pin}\n"
    return command

print()
dio_port = '/dev/ttyACM0'
with serial.Serial(dio_port) as mcu:
    def run_command(command: str):
        time.sleep(0.005)
        print(f"Running command: {command}")
        mcu.write(command.encode())
        time.sleep(0.005)
        res = mcu.read(mcu.in_waiting).decode()
        print(f"res: '{res}'")
        parts = res.split("\n")
        print(parts)
        if len(parts) > 1:
            res = parts[1].strip("\r")
        return res

    def handler(query: gedge.TagWriteQuery) -> None:
        if query.value == True:
            command = open_vice_command(0, 0)
            res = run_command(command)
        elif query.value == False:
            command = close_vice_command(0, 0)
            res = run_command(command)
        query.reply(200)

    here = pathlib.Path(__file__).parent
    config = gedge.NodeConfig.from_json5(str(here / "edge.json5"))
    config.add_tag_write_handler("vice/open", handler=handler)

    with gedge.connect(config, "tcp/192.168.4.60:7447") as session:
        # read initial value of vice
        command = read_vice_state_command(0, 0)
        state = run_command(command)
        initial_value = False if state == '1' else True
        session.update_tag("vice/open", initial_value)
        print(f"initial value of vice is {initial_value}")

        while True:
            pass
