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

    config = gedge.EdgeNodeConfig('BuildAtScale/Robots/Arms', name="Daisy")
    config.add_tag("tm12/joint_pos", list[float], properties={'eng_units': 'deg'})
    config.add_tag("project/is_running", bool, properties={'Description': 'True if a project is running, false if not'})
    with gedge.connect(config) as session:
        session: gedge.EdgeNodeSession
        i = 0
        while i < 10:
            if i % 2:
                session.update_tag("project/is_running", True)

            joint_pos = pull_joint_pos()
            buf = f"{joint_pos}"
            print(f"Putting Data ('tm12/joint_pos': '{buf}')")
            session.update_tag("tm12/joint_pos", joint_pos)
            time.sleep(1)
            i += 1
        session.send_state(False)
        time.sleep(3)
