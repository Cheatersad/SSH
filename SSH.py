#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Updated function to collect data from a node with new commands
def collect_data_from_node_updated(node):
    # Connect to the node via SSH
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(node['host'], username=node['username'], password=node['password'])
    
    # Commands mapping to their respective data points
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

    # Collect data using the commands
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

    # Close the SSH connection
    client.close()

    return collected_data

# Update the fields for the CSV file to include new metrics
def save_data_to_csv_updated(data, filename):
    fields = [
        'region', 'node_name', 'date', 'day_of_the_week', 'time', 'cpu_load', 'memory_load',
        'subscriber_count_registered', 'subscriber_count_deregistered',
        'subscriber_count_connected', 'subscriber_count_idle',
        'subscriber_count_amfRmState_registered', 'subscriber_count_amfRmState_deregistered',
        'subscriber_count_amfCmState_connected', 'subscriber_count_amfCmState_idle',
        'amfIntfSummary_N2', 'intfSummary_s1mme'
    ]
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Update main function to use the updated functions
def main_updated():
    all_data = collect_data_from_all_nodes(nodes)  # Reuse the function as it calls collect_data_from_node internally
    save_data_to_csv_updated(all_data, 'node_data_updated.csv')


main_updated()


# In[ ]:




