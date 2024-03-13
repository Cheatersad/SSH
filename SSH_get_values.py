import paramiko
import json
import csv

# Nodes details
nodes = [
    {"region": "Espoo", "name": "TCmm-Nike-SRN-Espoo", "host": "10.27.211.225", "username": "cmm", "password": "SRNcwwUser12!"},
    {"region": "Espoo", "name": "TAMF-Jill-SRN-Espoo", "host": "10.27.211.219", "username": "cmm", "password": "SRNcwwUser1!"}
]

# Command details
commands = [
    "cmm subscriber count --emmState registered -f json",
    "cmm subscriber count --emmState deregistered -f json",
    "cmm subscriber count --ecmState connected -f json",
    "cmm subscriber count --ecmState idle -f json",
    "cmm subscriber count --amfRmState registered -f json",
    "cmm subscriber count --amfRmState deregistered -f json",
    "cmm subscriber count --amfCmState connected -f json",
    "cmm subscriber count --amfCmState idle -f json",
    "cmm amfIntfSummary list --amfIntfType N2 -f json",
    "cmm intfSummary list --linkInterfaceType s1mme -f json"
]

def parse_json_for_column(output, key):
    """Generalized function to extract values from JSON command output."""
    try:
        data = json.loads(output)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get('Field') == key:
                    return str(item.get('Value', '0'))
        elif isinstance(data, dict):
            return str(data.get(key, '0'))
        return "0"
    except json.JSONDecodeError:
        return "0"

def parse_json_link_count(output):
    """Extracts N2 link counts from JSON command output."""
    try:
        data = json.loads(output)
        enabled_count, disabled_count = 0, 0
        # Assuming 'data' is a list of dictionaries
        for item in data:
            if item.get('linkOperationState') == 'enabled':
                enabled_count += int(item.get('linkCount', 0))
            elif item.get('linkOperationState') == 'disabled':
                disabled_count += int(item.get('linkCount', 0))
        total = enabled_count + disabled_count
        return str(enabled_count), str(disabled_count), str(total)
    except json.JSONDecodeError:
        return "0", "0", "0"

def collect_metrics_for_node(client, node):
    data_collection = {"Region": node["region"], "Node Name": node["name"]}
    # Initialize placeholders for N2 counts
    n2_counts = {"N2_Enabled": 0, "N2_Disabled": 0, "N2_Total": 0}

    for command in commands:
        result = execute_ssh_command(client, command)
        command_key = command.split('--')[1].split('-')[0].strip().replace(' ', '_')
        
        if 'intfSummary' in command or 'amfIntfSummary' in command:
            enabled, disabled, total = parse_json_link_count(result)
            # Aggregate N2 counts directly instead of appending
            n2_counts["N2_Enabled"] += int(enabled)
            n2_counts["N2_Disabled"] += int(disabled)
            n2_counts["N2_Total"] += int(total)
        else:
            # For subscriber count commands
            sum_value = parse_json_for_column(result, "Sum")
            data_collection[command_key] = sum_value
    
    # After processing all commands, add N2 counts to the collection
    data_collection.update(n2_counts)
    return data_collection

def execute_ssh_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    return stdout.read().decode().strip()

def collect_data_and_write_to_csv(nodes, filename):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    all_data = []

    for node in nodes:
        client.connect(node['host'], username=node['username'], password=node['password'])
        node_data = collect_metrics_for_node(client, node)
        all_data.append(node_data)
        client.close()

    # Determine the command-specific fields, ignoring 'Region' and 'Node Name' for now
    command_fields = [key for key in all_data[0].keys() if key not in ('Region', 'Node Name') and not key.startswith('N2_')]

    # Ensure the order starts with 'Region', 'Node Name', followed by command fields, and ends with link counts
    fields = ['Region', 'Node Name'] + command_fields + ['N2_Enabled', 'N2_Disabled', 'N2_Total']

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for data_row in all_data:
            writer.writerow(data_row)

def main():
    collect_data_and_write_to_csv(nodes, 'node_metrics_final.csv')

if __name__ == "__main__":
    main()
