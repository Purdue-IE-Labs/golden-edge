import pathlib
import gedge

import serial
import time

import threading

print()
DIO_PORT = '/dev/ttyACM0'

def run_command(command: str):
    time.sleep(0.005)
    print(f"Running command: {command}")

    with serial.Serial(DIO_PORT) as mcu:
        mcu.write(command.encode())
        time.sleep(0.005)
        res = mcu.read(mcu.in_waiting).decode()

    print(f"res: '{res}'")
    parts = res.split("\n")
    if len(parts) > 1:
        res = parts[1].strip("\r")
    return res

def open_vice_command(group: int = 0, pin: int = 0) -> str:
    command = f"dio set DO_G{group} {pin} false\n"
    return command

def close_vice_command(group: int = 0, pin: int = 0) -> str:
    command = f"dio set DO_G{group} {pin} true\n"
    return command

def read_vice_state_command(group: int = 0, pin: int = 0) -> str:
    command = f"dio get DO_G{group} output {pin}\n"
    return command

def read_vice_mode_command(group: int = 0, pin: int = 0) -> str:
    command = f"dio get DI_G{group} input {pin}\n"
    return command

def handler(query: gedge.TagWriteQuery) -> None:
    if get_mode() == False:
        # manual mode, we cannot update the state of the vice
        query.reply(400)
        return

    state = query.value
    if state:
        command = open_vice_command(0, 0)
    else:
        command = close_vice_command(0, 0)
    run_command(command)
    query.reply(200)

def get_mode() -> bool:
    command = read_vice_mode_command(0, 0)
    state = run_command(command)
    mode = False if state == '1' else True
    return mode

def update_mode():
    mode = get_mode()
    session.update_tag("mode/robot", mode)
    return mode

def update_vice_state():
    command = read_vice_state_command(0, 0)
    state = run_command(command)
    value = False if state == '1' else True
    session.update_tag("vice/open", value)
    return value

def start_mode_checking(every: int = 1000):
    def update_mode_periodic():
        while True:
            update_mode()
            time.sleep(every / 1000)

    # daemon thread so that, when main program ends, this thread 
    # ends automatically
    thread = threading.Thread(target=update_mode_periodic, daemon=True)
    thread.start()

    return thread

here = pathlib.Path(__file__).parent
config = gedge.NodeConfig.from_json5(str(here / "edge.json5"))
config.add_tag_write_handler("vice/open", handler=handler)

with gedge.connect(config, "tcp/192.168.4.60:7447") as session:
    # read initial value of vice
    state = update_vice_state()
    print(f"initial value of vice is {state}")

    # new tag: is vice in robot or manual mode
    mode = update_mode()
    print(f"initial value of mode if {mode}")

    start_mode_checking(every=5000)

    while True:
        pass
