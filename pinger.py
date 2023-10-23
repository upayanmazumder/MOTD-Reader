import tkinter as tk
import socket
import json
import requests
import html
import discord_webhook
from discord_webhook import DiscordWebhook, DiscordEmbed
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Retrieve the Discord webhook URL from the environment variables
discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

# Function to resolve a domain to an IP address
def resolve_domain(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return None

# Function to fetch server details from a Minecraft server
def fetch_server_details(ip, port):
    try:
        # Make a request to the mcsrvstat.us API to get server details
        response = requests.get(f"https://api.mcsrvstat.us/2/{ip}:{port}")
        data = json.loads(response.text)
        return data
    except requests.exceptions.RequestException:
        return None

# Function to parse Minecraft color codes and replace HTML entities
def parse_color_codes(text):
    # Minecraft color code to HTML color name mapping
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

# Function to send a message to the Discord webhook as an embed with Minecraft-style formatting
def send_motd_to_discord(message, ip, port, players_online):
    webhook = DiscordWebhook(url=discord_webhook_url)
    embed = DiscordEmbed(title=f"Server: {ip}:{port}", color=242424)
    embed.set_footer(text="Minecraft Server MOTD")
    
    # Use monospaced font for Minecraft-style formatting
    embed.add_embed_field(name="MOTD", value=f"```fix\n{message}```")
    
    # Add the number of players online
    embed.add_embed_field(name="Players Online", value=str(players_online))
    
    webhook.add_embed(embed)
    response = webhook.execute()

    if response.status_code == 204:
        print("Message sent to Discord successfully")
    else:
        print(f"Failed to send message to Discord. Status code: {response.status_code}")

# Function to update the MOTD label
def update_motd_label():
    # Get server IP and port from input fields
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
            players_online = server_details.get("players", {}).get("online", "N/A")
            motd_text.delete(1.0, tk.END)  # Clear the text widget
            motd_text.insert(tk.END, formatted_motd)

            # Send the MOTD to Discord as an embed with Minecraft-style formatting
            send_motd_to_discord(formatted_motd, ip, port, players_online)
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
