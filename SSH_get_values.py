#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Import necessary libraries
import paramiko
from datetime import datetime
import csv

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
        output = stdout.read().decode().strip()
        # Process output based on command type
        if key.startswith('subscriber_count'):
            # Assuming the sum is always in the last line after 'Total'
            sum_line = output.split('\n')[-1]  # Last line where total should be
            sum_value = sum_line.split()[-1]  # Assuming sum is the last word
            collected_data[key] = sum_value
        elif key in ['amfIntfSummary_N2', 'intfSummary_s1mme']:
            # Assuming there are lines for enabled and disabled, extract numbers
            for line in output.split('\n'):
                if 'enabled' in line:
                    collected_data[f"{key}_enabled"] = line.split()[-1]
                elif 'disabled' in line:
                    collected_data[f"{key}_disabled"] = line.split()[-1]
            # Calculate sum of enabled and disabled
            total = int(collected_data[f"{key}_enabled"]) + int(collected_data[f"{key}_disabled"])
            collected_data[f"{key}_total"] = str(total)
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
    fields = ['region', 'node_name', 'date', 'day_of_the_week', 'time',
              'subscriber_count_registered', 'subscriber_count_deregistered', 'subscriber_count_connected', 
              'subscriber_count_idle', 'subscriber_count_amfRmState_registered', 
              'subscriber_count_amfRmState_deregistered', 'subscriber_count_amfCmState_connected', 
              'subscriber_count_amfCmState_idle', 'amfIntfSummary_N2_enabled', 'amfIntfSummary_N2_disabled',
              'amfIntfSummary_N2_total', 'intfSummary_s1mme_enabled', 'intfSummary_s1mme_disabled',
              'intfSummary_s1mme_total']
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Main function to coordinate data collection and storage
def main():
    all_data = collect_data_from_all_nodes(nodes)
    save_data_to_csv(all_data, 'node_data.csv')

# Note: Uncomment the below lines when you are ready to run the program
# main()

