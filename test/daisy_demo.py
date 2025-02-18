from pymodbus.client import ModbusTcpClient
import gedge
import struct
import time

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

    config = gedge.NodeConfig('BuildAtScale/Robots/Arms')
    config.add_tag("tm12/joint_pos", list[float], props={'eng_units': 'deg'})
    config.add_tag("project/is_running", bool, props={'Description': 'True if a project is running, false if not'})
    with gedge.connect(config) as session:
        while True:
            joint_pos = pull_joint_pos()
            session.update_tag("tm12/joint_pos", joint_pos)
            time.sleep(1)
