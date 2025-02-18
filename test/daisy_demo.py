import math
from pymodbus.client import ModbusTcpClient
import gedge
import struct
import time
import sys

def pull_joint_pos():
    def decode_registers_to_deg(registers: list[int]) -> list[float]:
        # Each joint has 2 registers, pair them up in a list of lists
        register_pairs = [registers[i:i+2] for i in range(0, len(registers), 2)]
        # Converts list of register pairs to a list of floats representing the joint angle in degrees
        floats = [
            struct.unpack('>f', struct.pack('>HH', pair[0], pair[1]))[0]
            for pair in register_pairs
        ]
        return floats

    result = client.read_input_registers(address=7013, count=12, slave=1)
    deg_list = decode_registers_to_deg(result.registers)
    return deg_list


if __name__ == "__main__":
    # Modbus Connection
    host = '127.0.0.1'
    client = ModbusTcpClient(host)
    if not client.connect():
        raise ConnectionError(f"Unable to connect to Modbus server at {host}")
    
    print("ZENOH DAISY TELEMETRY DEMO\n")
    # Hide cursor
    print('\033[?25l', end="")

    config = gedge.NodeConfig('BuildAtScale/Robots/Arms')
    config.add_tag("tm12/joint_pos", list[float], props={'eng_units': 'deg'})
    # config.add_tag("project/is_running", bool, props={'Description': 'True if a project is running, false if not'})
    with gedge.connect(config) as session:
        print("Publishing data from BuildAtScale/Robots/Arms...\n")
        joint_names = [f"J{i}" for i in range(1,7)]
        joint_names = [f"{x:>8}" for x in joint_names]
        print(f"              {joint_names[0]}{joint_names[1]}{joint_names[2]}{joint_names[3]}{joint_names[4]}{joint_names[5]}")
        while True:
            joint_pos = pull_joint_pos()
            session.update_tag("tm12/joint_pos", joint_pos)
            joint_pos = [f"{x:8.2f}" for x in joint_pos]
            sys.stdout.write(f"\rjoint values: {joint_pos[0]}{joint_pos[1]}{joint_pos[2]}{joint_pos[3]}{joint_pos[4]}{joint_pos[5]}")
            sys.stdout.flush()
            time.sleep(0.05)
