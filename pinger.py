import tkinter as tk
import socket
import json
import requests
import html

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

# Function to parse Minecraft color codes and replace HTML entities
def parse_color_codes(text):
    color_map = {
        '0': 'black',
        '1': 'dark blue',
        '2': 'dark green',
        '3': 'dark aqua',
        '4': 'dark red',
        '5': 'dark purple',
        '6': 'gold',
        '7': 'gray',
        '8': 'dark gray',
        '9': 'blue',
        'a': 'green',
        'b': 'aqua',
        'c': 'red',
        'd': 'light purple',
        'e': 'yellow',
        'f': 'white',
    }
    
    # If MOTD is a list, join its elements into a single string
    if isinstance(text, list):
        text = ' '.join(text)

    # Replace HTML entities with their corresponding characters
    text = html.unescape(text)

    components = text.split('§')
    parsed_text = components[0]
    for component in components[1:]:
        color_code = component[0]
        if color_code in color_map:
            color_name = color_map[color_code]
            parsed_text += f'<font color="{color_name}">{component[1:]}</font>'
        else:
            parsed_text += f'§{component}'
    return parsed_text

# Function to update the MOTD label
def update_motd_label():
    server_ip = ip_entry.get()
    port = port_entry.get()

    if ':' in server_ip:
        ip, port = server_ip.split(':')
    else:
        ip = resolve_domain(server_ip)

    if not ip:
        motd_text.delete(1.0, tk.END)  # Clear the text widget
        motd_text.insert(tk.END, "Invalid IP or Domain")
    else:
        server_details = fetch_server_details(ip, port)
        if server_details:
            motd = server_details.get("motd", {}).get("clean", "N/A")  # Get the "clean" MOTD
            formatted_motd = parse_color_codes(motd)
            motd_text.delete(1.0, tk.END)  # Clear the text widget
            motd_text.insert(tk.END, formatted_motd)
        else:
            motd_text.delete(1.0, tk.END)  # Clear the text widget
            motd_text.insert(tk.END, "Server not found")

# Create the main window
window = tk.Tk()
window.title("Minecraft Server MOTD")

# Apply Minecraft-style colors and fonts
bg_color = '#000000'  # Background color
fg_color = '#55FF55'  # Text color
font = ('Minecraft', 12)

# Configure the window appearance
window.configure(bg=bg_color)

# Create and place labels and input fields with Minecraft-like styles
ip_label = tk.Label(window, text="Server IP/Domain:", bg=bg_color, fg=fg_color, font=font)
ip_label.pack()
ip_entry = tk.Entry(window)
ip_entry.pack()
port_label = tk.Label(window, text="Port (Default: 25565):", bg=bg_color, fg=fg_color, font=font)
port_label.pack()
port_entry = tk.Entry(window)
port_entry.insert(0, "25565")  # Default port
port_entry.pack()

# Create a Text widget for the MOTD
motd_text = tk.Text(window, wrap=tk.WORD, height=5, width=40, bg=bg_color, fg=fg_color, font=font)
motd_text.pack()

# Create and place the "Get MOTD" button
get_motd_button = tk.Button(window, text="Get MOTD", command=update_motd_label, bg=bg_color, fg=fg_color, font=font)
get_motd_button.pack()

# Start the GUI application
window.mainloop()
