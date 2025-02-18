from pymodbus.client import ModbusTcpClient
import gedge
import sys

def on_joint_pos(key_expr: str, data: list[float]):
    joint_pos = [f"{x:8.2f}" for x in data]
    sys.stdout.write(f"\rjoint values: {joint_pos[0]}{joint_pos[1]}{joint_pos[2]}{joint_pos[3]}{joint_pos[4]}{joint_pos[5]}")
    sys.stdout.flush()

if __name__ == "__main__":
    print("ZENOH DAISY TELEMETRY DEMO\n")

    # Hide cursor
    print('\033[?25l', end="")

    config = gedge.NodeConfig('BuildAtScale/Robots/Watcher')
    with gedge.connect(config) as session:
        print("Connecting to node BuildAtScale/Robots/Arms...\n")
        remote = session.connect_to_remote('BuildAtScale/Robots/Arms')

        joint_names = [f"J{i}" for i in range(1,7)]
        joint_names = [f"{x:>8}" for x in joint_names]
        print(f"              {joint_names[0]}{joint_names[1]}{joint_names[2]}{joint_names[3]}{joint_names[4]}{joint_names[5]}")
        remote.add_tag_data_callback("tm12/joint_pos", on_joint_pos)
        while True:
            pass
