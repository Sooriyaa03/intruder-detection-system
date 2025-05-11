import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import os
import uuid
import serial
import time

class SecuritySystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Intruder Detection System")

        self.data_folder = "detected_images"
        os.makedirs(self.data_folder, exist_ok=True)

        self.image_list_frame = ttk.LabelFrame(root, text="Detected Intruders")
        self.image_list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.canvas = tk.Canvas(self.image_list_frame)
        self.scrollbar = ttk.Scrollbar(self.image_list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.image_rows = {} # Dictionary to store row widgets and image paths
        self.serial_port = None

        try:
            self.serial_port = serial.Serial('COM7', 9600) # Replace 'COM3' with the Arduino's serial port
            print("Serial port connected.")
            self.read_serial_data()
        except serial.SerialException as e:
            messagebox.showerror("Serial Error", f"Could not open serial port: {e}")

        self.load_existing_images()

    def load_existing_images(self):
        for filename in os.listdir(self.data_folder):
            filepath = os.path.join(self.data_folder, filename)
            if os.path.isfile(filepath) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.add_image_row(filepath)

    def capture_and_display(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam.")
            return

        ret, frame = cap.read()
        cap.release()

        if ret:
            filename = f"detected_{uuid.uuid4().hex}.png"
            filepath = os.path.join(self.data_folder, filename)
            cv2.imwrite(filepath, frame)
            self.add_image_row(filepath)
            messagebox.showinfo("Intruder Detected", f"Intruder detected, image saved as {filename}")
        else:
            messagebox.showerror("Error", "Failed to capture image.")

    def read_serial_data(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                while self.serial_port.in_waiting > 0:
                    serial_data = self.serial_port.readline().decode('utf-8').strip()
                    print(f"Serial Raw Data: {serial_data}")
                    try:
                        distance = float(serial_data)
                        if distance <= 20:
                            self.capture_and_display()
                    except ValueError:
                        # Ignore non-integer output from serial
                        pass
                self.root.after(100, self.read_serial_data) # Check serial port every 100 ms
            except serial.SerialException as e:
                messagebox.showerror("Serial Error", f"Error reading from serial port: {e}")
                self.serial_port = None
        else:
            self.root.after(1000, self.read_serial_data) # Try to reconnect every 1 second

    def add_image_row(self, image_path):
        row_frame = ttk.Frame(self.scrollable_frame)
        row_frame.pack(pady=5, fill="x")

        try:
            img = Image.open(image_path)
            img.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(img)
            image_label = ttk.Label(row_frame, image=photo)
            image_label.image = photo  # Keep a reference!
            image_label.pack(side="left", padx=5)
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
            error_label = ttk.Label(row_frame, text="Error loading image")
            error_label.pack(side="left", padx=5)
            return

        expand_button = ttk.Button(row_frame, text="Expand", command=lambda p=image_path: self.expand_image(p))
        expand_button.pack(side="left", padx=5)

        safe_button = ttk.Button(row_frame, text="Safe", command=lambda p=image_path, rf=row_frame: self.mark_safe(p, rf))
        safe_button.pack(side="left", padx=5)

        self.image_rows[image_path] = row_frame

    def expand_image(self, image_path):
        try:
            img = Image.open(image_path)
            top = tk.Toplevel(self.root)
            top.title("Expanded Image")
            photo = ImageTk.PhotoImage(img)
            label = ttk.Label(top, image=photo)
            label.image = photo
            label.pack(padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image: {e}")

    def mark_safe(self, image_path, row_frame):
        if messagebox.askyesno("Confirm", "Mark as safe and delete?"):
            try:
                os.remove(image_path)
                row_frame.destroy()
                del self.image_rows[image_path]
                messagebox.showinfo("Success", "Image deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting image: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SecuritySystem(root)
    root.mainloop()