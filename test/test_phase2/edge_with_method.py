import math
from pymodbus.client import ModbusTcpClient
import gedge
import struct
import time
import sys
 
 
def pull_joint_pos():
    def decode_registers_to_deg(registers: list[int]) -> list[float]:
        # Each joint has 2 registers, pair them up in a list of lists
        register_pairs = [registers[i : i + 2] for i in range(0, len(registers), 2)]
        # Converts list of register pairs to a list of floats representing the joint angle in degrees
        floats = [
            struct.unpack(">f", struct.pack(">HH", pair[0], pair[1]))[0]
            for pair in register_pairs
        ]
        return floats
 
    result = client.read_input_registers(address=7013, count=12, slave=1)
    deg_list = decode_registers_to_deg(result.registers)
    return deg_list
 
 
def on_start_project():
    def string_to_registers(input_str) -> list[int]:
        num_registers = 99
        total_chars = num_registers * 2  # 198 characters
 
        if not isinstance(input_str, str):
            raise ValueError("Invalid input. Please provide a valid string.")
 
        # Pad with null characters if needed; if longer, truncate to total_chars.
        if len(input_str) < total_chars:
            input_str = input_str.ljust(total_chars, "\0")
        else:
            input_str = input_str[:total_chars]
 
        result = []
        # Process the string two characters at a time.
        for i in range(0, total_chars, 2):
            ascii1 = ord(input_str[i])
            ascii2 = ord(input_str[i + 1])
            combined = (
                ascii1 << 8
            ) | ascii2  # Combine the two ASCII codes into one 16-bit integer.
            result.append(combined)
 
        return result
 
    def registers_to_string(registers: list[int]) -> str:
        result_chars = []
 
        for reg in registers:
            # Stop at the first 0 register, which signifies the end of the string.
            if reg == 0:
                break
 
            # Extract the high and low bytes from the 16-bit integer.
            high_byte = (reg >> 8) & 0xFF
            low_byte = reg & 0xFF
            result_chars.append(chr(high_byte))
            result_chars.append(chr(low_byte))
 
        # Combine the characters into a string.
        result_string = "".join(result_chars)
 
        # Remove any trailing null characters.
        result_string = result_string.replace("\0", "")
        return result_string
 
    def method(query: gedge.MethodQuery):
        proj_name, speed = query.params["name"], query.params["speed"]

        # Check if project is running - FC:2, Addr: 7202
        result = client.read_discrete_inputs(address=7202, count=1, slave=1)
        proj_running = result.bits[0]
        if proj_running:
            print("Return Code 400: Fail, a project is already running")
            query.reply(400)
            return
        # TODO: Check if robot is in error before continuing
        # Check Remote Control Fieldbus Active (TM12S Only) - FC:02, Addr: 7212
        # TODO: Make sure this the correct register, the simulator seems to still take modbus commands with this being false.
        result = client.read_discrete_inputs(address=7212, count=1, slave=1)
        remote_fieldbus_active = result.bits[0]
        if not remote_fieldbus_active:
            # Return Code 401: Fail, remote fieldbus is not active (Not in Auto Remote Mode)
            print(
                "Return Code 401: Fail, remote fieldbus is not active (Not in Auto Remote Mode)"
            )
            query.reply(401)
            return
 
        # Change Current Project FC:16, Addr:7701~7799
        proj_name_registers = string_to_registers(proj_name)
        result = client.write_registers(
            address=7701, values=proj_name_registers, slave=1
        )
 
        # Check to make sure project name matches
        time.sleep(0.2)
        result = client.read_input_registers(address=7701, count=98, slave=1)
        active_project_name = registers_to_string(registers=result.registers)
 
        if active_project_name != proj_name:
            # Return Code 402: Fail, could not change project name
            print("Return Code 402: Fail, could not change project name")
            query.reply(402)
            return
 
        # Play Current Project FC:5, Addr: 7103
        result = client.write_coil(address=7103, value=True, slave=1)
 
        # Check to make sure project is playing
        time.sleep(0.2)
        result = client.read_discrete_inputs(address=7202, count=1, slave=1)
        proj_running = result.bits[0]
        if not proj_running:
            # Try again after 1 second
            time.sleep(1)
            result = client.read_discrete_inputs(address=7202, count=1, slave=1)
            proj_running = result.bits[0]
            if not proj_running:
                # Return Code 403: Cannot play project
                print("Return Code 403: Cannot play project")
                query.reply(403)
                return
 
        # Return Code 200: Project Successfully started
        print("Return Code 200: Project Successfully Started")
        query.reply(200)
 
        # TODO: Listen to TCP messages from within the flow to send as 201
 
        # Set Project Speed FC:6, 7101
        result = client.write_register(address=7101, value=speed, slave=1)
 
        # TODO: Make speed check async so it doesnt block proj_running
        # Check Project Speed FC:4, Addr: 7101
        time.sleep(2)
        result = client.read_input_registers(address=7101, count=1, slave=1)
        if result.registers[0] != speed:
            # Return Code 300: Warning, failed to set project speed
            print("Return Code 300: Warning, failed to set project speed")
            query.reply(300)
 
        # Wait for project to stop running on controller
        while proj_running:
            time.sleep(0.5)
            proj_running = client.read_discrete_inputs(
                address=7202, count=1, slave=1
            ).bits[0]
 
        # Check if project ended in Error, or through natural program end.
        is_in_error = client.read_discrete_inputs(address=7201, count=1, slave=1).bits[
            0
        ]
        if is_in_error:
            # Return Code 404: project ended with error
            print("Return Code 404: project ended with error")
            query.reply(404)
            return
        else:
            # Return Code 202: Project ended sucessfully
            print("Return Code 202: Project ended successfully")
            query.reply(202)
            return
 
    return method
 
 
if __name__ == "__main__":
    # Modbus Connection
    host = "127.0.0.1"
    client = ModbusTcpClient(host)
    if not client.connect():
        raise ConnectionError(f"Unable to connect to Modbus server at {host}")
 
    # name = "testing2"
    # speed = 80
    handler = on_start_project()
    config = gedge.NodeConfig("BuildAtScale/Robots/Methods/Demo/Callee")
    m = config.add_method("start/project", handler)
    m.add_params(name=str, speed=int)
    m.add_response(400, props={
        "desc": "Fail, a project is already running"
    })
    m.add_response(401, props={
        "desc": "Fail, remote fieldbus is not active (Not in Auto Remote Mode)"
    })
    m.add_response(402, props={
        "desc": "Fail, could not change project name"
    })
    m.add_response(403, props={
        "desc": "Cannot play project"
    })
    m.add_response(404, props={
        "desc": "project ended with error"
    })
    m.add_response(200, props={
        "desc": "Project Successfully Started"
    })
    m.add_response(201, props={
        "desc": "Reserved"
    })
    m.add_response(202, props={
        "desc": "Project ended successfully"
    })
    m.add_response(300, props={
        "desc": "Warning, failed to set project speed"
    })

    with gedge.connect(config) as session:
        while True:
            pass
 