import tkinter as tk
import socket
import json
import requests

# Function to resolve domain to IP
def resolve_domain(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return None

# Function to fetch server details
def fetch_server_details(ip, port):
    try:
        response = requests.get(f"https://api.mcsrvstat.us/2/{ip}:{port}")
        data = json.loads(response.text)
        return data
    except requests.exceptions.RequestException:
        return None

# Function to update the result label
def update_result():
    server_ip = ip_entry.get()
    port = port_entry.get()

    if ':' in server_ip:
        ip, port = server_ip.split(':')
    else:
        ip = resolve_domain(server_ip)

    if not ip:
        result_label.config(text="Invalid IP or Domain")
    else:
        server_details = fetch_server_details(ip, port)
        if server_details:
            motd = server_details.get("motd", "N/A")
            players = server_details.get("players", {})
            player_count = players.get("online", 0)
            max_players = players.get("max", 0)
            version = server_details.get("version", "N/A")
            result_label.config(text=f"Motd: {motd}\nPlayers: {player_count}/{max_players}\nVersion: {version}")
        else:
            result_label.config(text="Server not found")

# Create the main window
window = tk.Tk()
window.title("Minecraft Server Info")

# Create and place labels and input fields
ip_label = tk.Label(window, text="Server IP/Domain:")
ip_label.pack()
ip_entry = tk.Entry(window)
ip_entry.pack()
port_label = tk.Label(window, text="Port (Default: 25565):")
port_label.pack()
port_entry = tk.Entry(window)
port_entry.insert(0, "25565")  # Default port
port_entry.pack()

# Create and place the result label
result_label = tk.Label(window, text="", wraplength=300)
result_label.pack()

# Create and place the "Get Info" button
get_info_button = tk.Button(window, text="Get Info", command=update_result)
get_info_button.pack()

# Start the GUI application
window.mainloop()
