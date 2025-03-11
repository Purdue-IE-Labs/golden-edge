import pathlib
import gedge

import serial
import time

print()
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
        if len(parts) > 1:
            res = parts[1].strip("\r")
        return res

    # time.sleep(0.005)
    # mcu.write(b'\r\n')
    # time.sleep(0.005)
    # mcu.read(mcu.in_waiting)
    # # command = "dio num D1_G0 outputs\n"
    # # command = "history\n"
    # # command  = "device list\n"
    # # mcu.write(command.encode())
    # # time.sleep(0.005)
    # # res = mcu.read(mcu.in_waiting).decode()
    # # print(res)

    # # get output of DO_G0
    # command = "dio get DO_G0 output 0\n"
    # terminal_command(command)
    # # set DO_G0 to off, 0V
    # command = "dio set DO_G0 0 false\n"
    # terminal_command(command)

    # command = "dio get DO_G0 output 0\n"
    # terminal_command(command)


    def handler(query: gedge.TagWriteQuery) -> None:
        # attempt to close or open the vice
        if query.value == True:
            # open the vice
            command = "dio set DO_G0 0 false\n"
            terminal_command(command)
        elif query.value == False:
            # close the vice
            command = "dio set DO_G0 0 true\n"
            terminal_command(command)
        query.reply(200)

    here = pathlib.Path(__file__).parent
    config = gedge.NodeConfig.from_json5(str(here / "edge.json5"))
    config.add_tag_write_handler("vice/open", handler=handler)

    with gedge.connect(config, "tcp/192.168.4.60:7447") as session:
        # read initial value of vice
        command = "dio get DO_G0 output 0\n"
        state = terminal_command(command).strip('\n\r ')
        initial_value = False if state == '1' else True
        session.update_tag("vice/open", initial_value)
        print(f"initial value of vice is {initial_value}")

        while True:
            pass