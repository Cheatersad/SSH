import csv
import json
import re
import paramiko
import socket
import threading
from collections import defaultdict
from datetime import datetime
nodes = []
with open("AMF_CMM_2.csv", "r") as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    for row in reader:
        node = {
            "host": row[0].strip(),
            "name": row[1].strip(),
            "password": row[2].strip(),
            "username": row[4].strip()
        }
        nodes.append(node)

# Commands to execute
commands = [
    "date '+%Y-%m-%d %A %H:%M:%S'",
    "cmm subscriber count --emmState registered -f json",       
    "cmm subscriber count --emmState deregistered -f json",
    "cmm subscriber count --ecmState connected -f json",
    "cmm subscriber count --ecmState idle -f json",
    "cmm subscriber count --amfRmState registered -f json",
    "cmm subscriber count --amfRmState deregistered -f json",
    "cmm subscriber count --amfCmState connected -f json",
    "cmm subscriber count --amfCmState idle -f json",
    "cmm amfIntfSummary list --amfIntfType N2 -f json",
    "cmm amfIntfSummary list --amfIntfType N12 -f json",
    "cmm amfIntfSummary list --amfIntfType N8 -f json",
    "cmm amfIntfSummary list --amfIntfType N11 -f json",
    "cmm amfIntfSummary list --amfIntfType N15 -f json",
    "cmm subscriber count -f json",
    "cmm intfSummary list --linkInterfaceType s1mme -f json",
    "cmm multiLink list --linkInterfaceType s6ad -f json",
    "cmm multiLink list --linkInterfaceType s11 -f json",
    "cmm multiLink list --linkInterfaceType sgs -f json",
    "ls -l /data-pcmd/ | grep -i amf | tail -15",
    "ls -l /data-pcmd/ | grep -i sgsn | tail -15",
    "ls -l /data-pcmd/ | grep -i mme | tail -15"
]

expanded_command_to_field_map = {
    "date '+%Y-%m-%d %A %H:%M:%S'": ["Date", "Time", "Day of the week"],
    "cmm subscriber count --emmState registered -f json": "emmState_registered_subscriber_count",
    "cmm subscriber count --emmState deregistered -f json": "emmState_deregistered_subscriber_count",
    "cmm subscriber count --ecmState connected -f json": "ecmState_connected_subscriber_count",
    "cmm subscriber count --ecmState idle -f json": "ecmState_idle_subscriber_count",
    "cmm subscriber count --amfRmState registered -f json": "amfRmState_registered_subscriber_count",
    "cmm subscriber count --amfRmState deregistered -f json": "amfRmState_deregistered_subscriber_count",
    "cmm subscriber count --amfCmState connected -f json": "amfCmState_connected_subscriber_count",
    "cmm subscriber count --amfCmState idle -f json": "amfCmState_idle_subscriber_count",
    "cmm subscriber count -f json": "subscriber_count",
    "cmm amfIntfSummary list --amfIntfType N2 -f json": ["N2_enabled", "N2_disabled", "N2_total"],
    "cmm amfIntfSummary list --amfIntfType N12 -f json": ["N12_enabled", "N12_disabled", "N12_total"],
    "cmm amfIntfSummary list --amfIntfType N8 -f json": ["N8_enabled", "N8_disabled", "N8_total"],
    "cmm amfIntfSummary list --amfIntfType N11 -f json": ["N11_enabled", "N11_disabled", "N11_total"],
    "cmm amfIntfSummary list --amfIntfType N15 -f json": ["N15_enabled", "N15_disabled", "N15_total"],
    "cmm intfSummary list --linkInterfaceType s1mme -f json": ["s1mme_enabled", "s1mme_disabled", "s1mme_total"],
    "cmm multiLink list --linkInterfaceType s6ad -f json": ["s6ad_enabled", "s6ad_disabled", "s6ad_total"],
    "cmm multiLink list --linkInterfaceType s11 -f json": ["s11_enabled", "s11_disabled", "s11_total"],
    "cmm multiLink list --linkInterfaceType sgs -f json": ["sgs_enabled", "sgs_disabled", "sgs_total"],
    "ls -l /data-pcmd/ | grep -i amf | tail -15": "NT_AMF_PCMD",
    "ls -l /data-pcmd/ | grep -i sgsn | tail -15": "NT_SGSN_PCMD",
    "ls -l /data-pcmd/ | grep -i mme | tail -15": "NT_MME_PCMD"
}

fieldnames = [
    "Node Name", "Date", "Time", "Day of the week",
    "emmState_registered_subscriber_count", "emmState_deregistered_subscriber_count",
    "ecmState_connected_subscriber_count", "ecmState_idle_subscriber_count",
    "amfRmState_registered_subscriber_count", "amfRmState_deregistered_subscriber_count",
    "amfCmState_connected_subscriber_count", "amfCmState_idle_subscriber_count",
    "subscriber_count", "N2_enabled", "N2_disabled", "N2_total",
    "N12_enabled", "N12_disabled", "N12_total", "N8_enabled", "N8_disabled", "N8_total",
    "N11_enabled", "N11_disabled", "N11_total", "N15_enabled", "N15_disabled", "N15_total",
    "s1mme_enabled", "s1mme_disabled", "s1mme_total", "s6ad_enabled", "s6ad_disabled", "s6ad_total",
    "s11_enabled", "s11_disabled", "s11_total", "sgs_enabled", "sgs_disabled", "sgs_total", "NT_AMF_PCMD",
    "NT_SGSN_PCMD", "NT_MME_PCMD"
]

def execute_ssh_command(ip, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    ssh.close()
    return output

def process_output(command, output, ssh, node):
    if command == "date '+%Y-%m-%d %A %H:%M:%S'":
        date, day_of_week, time = output.split()
        return [date, time, day_of_week]
    elif command.startswith("cmm subscriber count"):
        data = json.loads(output)
        for item in data:
            if item["Field"] == "Sum":
                return item["Value"]
    elif command.startswith("cmm amfIntfSummary list") or command.startswith("cmm intfSummary list"):
        data = json.loads(output)
        enabled_count = 0
        disabled_count = 0
        for item in data:
            if item["linkOperationState"] == "enabled":
                enabled_count += int(item["linkCount"])
            elif item["linkOperationState"] == "disabled":
                disabled_count += int(item["linkCount"])
        total_count = enabled_count + disabled_count
        return [enabled_count, disabled_count, total_count]
    elif command.startswith("cmm multiLink list"):
        data = json.loads(output)
        enabled_count = 0
        disabled_count = 0
        for item in data:
            if item["linkOperationState"] == "enabled":
                enabled_count += 1
            elif item["linkOperationState"] == "disabled":
                disabled_count += 1
        total_count = enabled_count + disabled_count
        return [enabled_count, disabled_count, total_count]
    elif command.startswith("ls -l /data-pcmd/ | grep -i"):
        files = re.findall(r'\S+\.zst', output)
        total_count = 0
        for file in files:
            zstdcat_command = f"zstdcat /data-pcmd/{file} | wc -l"
            count_output = execute_ssh_command(node["host"], node["username"], node["password"], zstdcat_command)
            total_count += int(count_output.strip())
        return total_count



def process_node(node, data_dict, lock):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(node["host"], username=node["username"], password=node["password"], timeout=30)
    except paramiko.AuthenticationException as e:
        error_message = f"Authentication failed for {node['host']}: {str(e)}"
        print(error_message)
        with lock:
            data_dict["errors"].append(error_message)
        return
    except (paramiko.SSHException, socket.error) as e:
        error_message = f"Connection failed for {node['host']}: {str(e)}"
        print(error_message)
        with lock:
            data_dict["errors"].append(error_message)
        return
    except Exception as e:
        error_message = f"An error occurred while connecting to {node['host']}: {str(e)}"
        print(error_message)
        with lock:
            data_dict["errors"].append(error_message)
        return

    row_data = {"Node Name": node["name"]}

    for command in commands:
        try:
            output = execute_ssh_command(node["host"], node["username"], node["password"], command)
            if command in expanded_command_to_field_map:
                field_names = expanded_command_to_field_map[command]
                if isinstance(field_names, list):
                    values = process_output(command, output, ssh, node)
                    for field_name, value in zip(field_names, values):
                        row_data[field_name] = value
                else:
                    single_value = process_output(command, output, ssh, node)
                    row_data[field_names] = single_value
        except Exception as e:
            error_message = f"An error occurred while executing command '{command}' on {node['host']}: {str(e)}"
            print(error_message)
            with lock:
                data_dict["errors"].append(error_message)
            continue

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with lock:
        data_dict["data"][current_time] = row_data

    ssh.close()

output_file = "output_testing.csv"
data_dict = defaultdict(dict)
data_dict["errors"] = []
lock = threading.Lock()

threads = []
for node in nodes:
    thread = threading.Thread(target=process_node, args=(node, data_dict, lock))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

with open(output_file, mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["Timestamp"] + fieldnames)
    writer.writeheader()

    for timestamp, row_data in data_dict["data"].items():
        row_data["Timestamp"] = timestamp
        writer.writerow(row_data)

with open("error.log", "w") as error_log:
    for error in data_dict["errors"]:
        error_log.write(error + "\n")
