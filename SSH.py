# Import necessary libraries
import paramiko
import csv
from datetime import datetime

# Define the nodes and credentials
nodes = [
    {"region": "Espoo", "name": "Nalla", "host": "nalla_host", "username": "user", "password": "pass"},
]

# Define a function to collect data from a node
def collect_data_from_node(node):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(node['host'], username=node['name'], password=node['password'])
    commands = {
        "cpu_load": "get_cpu_load",
        "memory_load": "get_memory_load",
        "subscriber_count_registered": "cmm subscriber count --emmState registered",
        "subscriber_count_deregistered": "cmm subscriber count --emmState deregistered",
        "subscriber_count_connected": "cmm subscriber count --ecmState connected",
        "subscriber_count_idle": "cmm subscriber count --ecmState idle",
        "subscriber_count_amfRmState_registered": "cmm subscriber count --amfRmState registered",
        "subscriber_count_amfRmState_deregistered": "cmm subscriber count --amfRmState deregistered",
        "subscriber_count_amfCmState_connected": "cmm subscriber count --amfCmState connected",
        "subscriber_count_amfCmState_idle": "cmm subscriber count --amfCmState idle",
        "amfIntfSummary_N2": "cmm amfIntfSummary list --amfIntfType N2",
        "intfSummary_s1mme": "cmm intfSummary list --linkInterfaceType s1mme"
    }
    collected_data = {
        "region": node['region'],
        "node_name": node['name'],
        "date": datetime.now().strftime("%d-%m-%Y"),
        "day_of_the_week": datetime.now().strftime("%A"),
        "time": datetime.now().strftime("%H:%M"),
    }
    for key, command in commands.items():
        stdin, stdout, stderr = client.exec_command(command)
        collected_data[key] = stdout.read().decode().strip()
    client.close()
    return collected_data

# Define a function to collect data from all nodes
def collect_data_from_all_nodes(nodes):
    all_data = []
    for node in nodes:
        node_data = collect_data_from_node(node)
        all_data.append(node_data)
    return all_data

# Define a function to save data to a CSV file
def save_data_to_csv(data, filename):
    fields = ['region', 'node_name', 'date', 'day_of_the_week', 'time', 'cpu_load', 'memory_load', 
              'subscriber_count_registered', 'subscriber_count_deregistered', 'subscriber_count_connected', 
              'subscriber_count_idle', 'subscriber_count_amfRmState_registered', 
              'subscriber_count_amfRmState_deregistered', 'subscriber_count_amfCmState_connected', 
              'subscriber_count_amfCmState_idle', 'amfIntfSummary_N2', 'intfSummary_s1mme']
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Main function to coordinate data collection and storage
def main():
    all_data = collect_data_from_all_nodes(nodes)
    save_data_to_csv(all_data, 'node_data.csv')
