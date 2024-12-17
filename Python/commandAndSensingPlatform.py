import tkinter as tk
import socket
import threading
import time
import re

# Constants
BT_ADDRESS = "7C:87:CE:27:D6:36"
PORT = 1
BT_DELAY = 0.075  # Global Bluetooth delay in seconds

class MotorControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Motor Control")

        # Command time mode
        self.command_time_mode = "Set"  # Modes: "Open", "Set"
        self.command_time = 25  # Default command time in milliseconds

        # Initialize Bluetooth connection
        self.bluetooth_socket = None
        self.running = True
        self.speed_adjust_motor = None  # Track which motor is selected for speed adjustment
        self.bt_connected = False  # Bluetooth connection status

        # Start Bluetooth thread
        self.bt_thread = threading.Thread(target=self.start_bluetooth)
        self.bt_thread.daemon = True
        self.bt_thread.start()

        # Start thread to read Bluetooth data
        self.bt_read_thread = threading.Thread(target=self.parse_bluetooth_data)
        self.bt_read_thread.daemon = True
        self.bt_read_thread.start()

       # GUI Elements
        self.bt_status_label = tk.Label(root, text="Bluetooth Status: Not Connected", fg="red")
        self.bt_status_label.pack()

        self.f_label = tk.Label(root, text="F: N/A", font=("Arial", 12))
        self.f_label.pack()

        self.g_label = tk.Label(root, text="G: N/A", font=("Arial", 12))
        self.g_label.pack()

        self.h_label = tk.Label(root, text="H: N/A", font=("Arial", 12))
        self.h_label.pack()

        self.bt_data_text = tk.Text(root, height=10, width=60, state="disabled")
        self.bt_data_text.pack(pady=10)

        # Bluetooth Raw Data Display
        self.bt_data_text = tk.Text(root, height=10, width=60, state="disabled")
        self.bt_data_text.pack(pady=10)

        # Start thread to read Bluetooth data
        self.bt_read_thread = threading.Thread(target=self.parse_bluetooth_data)
        self.bt_read_thread.daemon = True
        self.bt_read_thread.start()

        # Add notification for Z key functionality
        self.command_time_label = tk.Label(root, text="Hold 'Z' to adjust Command Time using +/-", fg="blue")
        self.command_time_label.pack()

        # Motor speed controls
        self.slider_values = [40, 40, 40, 40]  # Default values for motors 1-4
        self.sliders = []
        for i in range(4):
            label = tk.Label(root, text=f"Motor {i + 1} Speed")
            label.pack()

            slider = tk.Scale(root, from_=1, to=100, orient="horizontal", command=lambda val, idx=i: self.update_motor_speed(idx, val), length=600)
            slider.set(self.slider_values[i])
            slider.pack()
            self.sliders.append(slider)

        # Control buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        self.forward_button = tk.Button(self.button_frame, text="Forward")
        self.forward_button.bind("<ButtonPress>", lambda event: self.send_control_signal(1))
        self.forward_button.bind("<ButtonRelease>", lambda event: self.handle_button_release(0))
        self.forward_button.grid(row=0, column=1, padx=5, pady=5)

        self.backward_button = tk.Button(self.button_frame, text="Backward")
        self.backward_button.bind("<ButtonPress>", lambda event: self.send_control_signal(2))
        self.backward_button.bind("<ButtonRelease>", lambda event: self.handle_button_release(0))
        self.backward_button.grid(row=1, column=1, padx=5, pady=5)

        self.turn_cw_button = tk.Button(self.button_frame, text="Turn CW")
        self.turn_cw_button.bind("<ButtonPress>", lambda event: self.send_control_signal(9))
        self.turn_cw_button.bind("<ButtonRelease>", lambda event: self.handle_button_release(0))
        self.turn_cw_button.grid(row=0, column=2, padx=5, pady=5)

        self.turn_ccw_button = tk.Button(self.button_frame, text="Turn CCW")
        self.turn_ccw_button.bind("<ButtonPress>", lambda event: self.send_control_signal(10))
        self.turn_ccw_button.bind("<ButtonRelease>", lambda event: self.handle_button_release(0))
        self.turn_ccw_button.grid(row=1, column=2, padx=5, pady=5)

        # Stop button
        self.stop_button = tk.Button(root, text="STOP", command=lambda: self.send_control_signal(0), bg="red", fg="white")
        self.stop_button.pack(pady=10)

        # Command mode toggle
        self.mode_label = tk.Label(root, text=f"Command Mode: {self.command_time_mode}")
        self.mode_label.pack()

        self.toggle_mode_button = tk.Button(root, text="Toggle Command Mode (Q)", command=self.toggle_command_mode)
        self.toggle_mode_button.pack(pady=10)

        # Command time slider
        self.command_time_slider = tk.Scale(root, from_=0, to=1000, orient="horizontal", label="Command Time (ms)", length=600, command=self.update_command_time)
        self.command_time_slider.set(self.command_time)
        self.command_time_slider.pack()

        # Key bindings
        self.root.bind("<Up>", lambda event: self.send_control_signal(1))
        self.root.bind("<KeyRelease-Up>", lambda event: self.handle_button_release(0))
        self.root.bind("<Down>", lambda event: self.send_control_signal(2))
        self.root.bind("<KeyRelease-Down>", lambda event: self.handle_button_release(0))
        self.root.bind("<Left>", lambda event: self.send_control_signal(10))
        self.root.bind("<KeyRelease-Left>", lambda event: self.handle_button_release(0))
        self.root.bind("<Right>", lambda event: self.send_control_signal(9))
        self.root.bind("<KeyRelease-Right>", lambda event: self.handle_button_release(0))
        self.root.bind("<KeyPress-q>", lambda event: self.toggle_command_mode())

        # Keyboard controls for motor-specific speed adjustment
        for i in range(1, 5):
            self.root.bind(f"<KeyPress-{i}>", lambda event, idx=i-1: self.set_speed_adjust_motor(idx))
            self.root.bind(f"<KeyRelease-{i}>", lambda event: self.clear_speed_adjust_motor())
        self.root.bind("<KeyPress-minus>", lambda event: self.adjust_speed(-1) if self.speed_adjust_motor is not None else self.adjust_command_time(-10))
        self.root.bind("<KeyPress-plus>", lambda event: self.adjust_speed(1) if self.speed_adjust_motor is not None else self.adjust_command_time(10))

        # Command time adjustment via keyboard
        self.root.bind("<KeyPress-z>", lambda event: self.set_command_time_adjust_mode(True))
        self.root.bind("<KeyRelease-z>", lambda event: self.set_command_time_adjust_mode(False))

        self.command_time_adjust_mode = False

    def start_bluetooth(self):
        """Establish the Bluetooth connection."""
        try:
            self.bluetooth_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            self.bluetooth_socket.connect((BT_ADDRESS, PORT))
            self.bt_connected = True
            self.update_bt_status("Connected", "green")
            print("Bluetooth connected")

            # Start reading Bluetooth data after connection
            self.bt_read_thread = threading.Thread(target=self.read_bluetooth_data)
            self.bt_read_thread.daemon = True
            self.bt_read_thread.start()
        except Exception as e:
            self.update_bt_status("Not Connected", "red")
            print(f"Bluetooth connection error: {e}")

    def read_bluetooth_data(self):
        """Continuously read Bluetooth data and process it."""
        while self.running and self.bluetooth_socket:
            try:
                # Read data from Bluetooth
                data = self.bluetooth_socket.recv(1024).decode("utf-8").strip()
                if data:
                    # Schedule GUI updates on the main thread
                    self.root.after(0, self.display_bluetooth_data, data)
                    self.root.after(0, self.parse_bluetooth_data, data)
            except Exception as e:
                print(f"Error reading Bluetooth data: {e}")
                break

    def parse_bluetooth_data(self, data):
        """Parse the incoming Bluetooth data using regular expressions."""
        try:
            match = re.match(r"([FGH])(\d+)", data)
            if match:
                channel = match.group(1)
                value = int(match.group(2))

                # Update the corresponding label based on the channel
                if channel == "F":
                    self.update_value_label(self.f_label, "Left (F)", value)
                elif channel == "G":
                    self.update_value_label(self.g_label, "Forward (G)", value)
                elif channel == "H":
                    self.update_value_label(self.h_label, "Right (H)", value)
            else:
                print(f"Unrecognized message format: {data}")
        except Exception as e:
            print(f"Error processing data: {data}, Error: {e}")

    def update_value_label(self, label, prefix, value):
        """Update a label with a new value."""
        label.config(text=f"{prefix}: {value}")

    def display_bluetooth_data(self, data):
        """Display raw Bluetooth data in the text widget."""
        self.bt_data_text.config(state="normal")
        self.bt_data_text.insert(tk.END, f"{data}\n")
        self.bt_data_text.see(tk.END)
        self.bt_data_text.config(state="disabled")

    def update_bt_status(self, status, color):
        """Update the Bluetooth status label."""
        self.bt_status_label.config(text=f"Bluetooth Status: {status}", fg=color)

    def initialize_speeds(self):
        """Initialize motor speeds with a delay and send a message."""
        time.sleep(2)  # 2-second delay
        self.send_initial_slider_values()
        print("Speeds initialized and sent to Bluetooth device.")

    def send_initial_slider_values(self):
        """Send the current slider values for Channels A-D upon successful Bluetooth connection."""
        for i, value in enumerate(self.slider_values):
            message = f"{chr(65 + i)}{value}\n"
            self.send_message(message)

    def update_motor_speed(self, motor_index, value):
        """Send motor speed update over Bluetooth."""
        self.slider_values[motor_index] = int(value)
        if self.bluetooth_socket:
            message = f"{chr(65 + motor_index)}{value}\n"
            self.send_message(message)

    def send_control_signal(self, control_value):
        """Send a control signal over Bluetooth."""
        if self.bluetooth_socket:
            message = f"E{control_value}\n"
            self.send_message(message)

    def handle_button_release(self, stop_signal):
        """Handle button release depending on the command time mode."""
        if self.command_time_mode == "Open":
            self.send_stop_signal_with_delay()
        elif self.command_time_mode == "Set":
            self.root.after(self.command_time, lambda: self.send_control_signal(stop_signal))

    def send_stop_signal_with_delay(self):
        """Send a stop signal after a slight delay."""
        if self.bluetooth_socket:
            time.sleep(BT_DELAY)  # Global Bluetooth delay
            self.send_control_signal(0)

    def send_message(self, message):
        """Send a message to the Bluetooth device."""
        try:
            self.bluetooth_socket.send(message.encode("utf-8"))
            print(f"{message.strip()}")
            time.sleep(BT_DELAY)  # Global Bluetooth delay between messages
        except Exception as e:
            print(f"Error sending message: {e}")

    def toggle_command_mode(self):
        """Toggle between Open and Set command modes."""
        self.command_time_mode = "Set" if self.command_time_mode == "Open" else "Open"
        self.mode_label.config(text=f"Command Mode: {self.command_time_mode}")

    def update_command_time(self, value):
        """Update the automatic command time from the slider."""
        self.command_time = int(value)

    def set_speed_adjust_motor(self, motor_index):
        """Set the motor index for speed adjustment."""
        self.speed_adjust_motor = motor_index

    def clear_speed_adjust_motor(self):
        """Clear the motor index for speed adjustment."""
        self.speed_adjust_motor = None

    def adjust_speed(self, increment):
        """Adjust the speed of the selected motor."""
        if self.speed_adjust_motor is not None:
            motor_index = self.speed_adjust_motor
            new_speed = max(1, min(100, self.slider_values[motor_index] + increment))
            self.slider_values[motor_index] = new_speed
            self.sliders[motor_index].set(new_speed)
            self.update_motor_speed(motor_index, new_speed)

    def set_command_time_adjust_mode(self, enable):
        """Enable or disable command time adjustment mode."""
        self.command_time_adjust_mode = enable

    def adjust_command_time(self, increment):
        """Adjust the command time if in adjustment mode."""
        if self.command_time_adjust_mode:
            new_time = max(0, min(1000, self.command_time + increment))
            self.command_time = new_time
            self.command_time_slider.set(new_time)

    def stop(self):
        """Clean up resources when the application is closed."""
        print("Closing application and cleaning up resources...")
        self.running = False  # Stop the Bluetooth reading thread

        # Close the Bluetooth socket safely
        if self.bluetooth_socket:
            try:
                self.bluetooth_socket.close()
                print("Bluetooth socket closed successfully.")
            except Exception as e:
                print(f"Error closing Bluetooth socket: {e}")

        # Destroy the Tkinter root window
        try:
            self.root.destroy()
            print("Application closed successfully.")
        except Exception as e:
            print(f"Error closing GUI: {e}")

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = MotorControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    root.mainloop()
