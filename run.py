import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from urllib import request
from threading import Thread
from datetime import datetime, timedelta

class FileDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Downloader")

        # Menonaktifkan kemampuan untuk mengubah ukuran jendela
        self.root.resizable(False, False)

        self.create_widgets()

        # Variable to track whether the download is paused
        self.paused = False

        # Variable to track whether the log window is open
        self.log_window_open = False

        # Variable to store download log
        self.download_log = []

        # Variable to store the download start time
        self.start_time = None

        # Variable to store the total file size
        self.total_size = 0

        # Variable to store the total downloaded size
        self.downloaded_size = 0

        # Variable to store the average download speed
        self.average_speed = 0

    def create_widgets(self):
        # Entry for the file URL
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky="ew")

        # Button to browse for the destination folder
        self.browse_button = tk.Button(self.root, text="Browse", command=self.browse_destination)
        self.browse_button.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky="ew")

        # Entry for the destination folder
        self.destination_entry = tk.Entry(self.root, width=40)
        self.destination_entry.grid(row=2, column=0, columnspan=5, padx=10, pady=10, sticky="ew")

        # Label to display download status
        self.status_label = tk.Label(self.root, text="")
        self.status_label.grid(row=3, column=0, columnspan=5, pady=10)

        # Label to display download percentage
        self.percent_label = tk.Label(self.root, text="")
        self.percent_label.grid(row=4, column=0, columnspan=5, pady=10)

        # Console to display download progress
        self.console = tk.Text(self.root, height=10, width=60)
        self.console.grid(row=6, column=0, columnspan=5, pady=10, sticky="ew")

        # Button to start the download
        self.download_button = tk.Button(self.root, text="Download", command=self.start_download)
        self.download_button.grid(row=7, column=0, pady=10, sticky="ew")

        # Button to pause the download
        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause_download, state=tk.DISABLED)
        self.pause_button.grid(row=7, column=1, pady=10, sticky="ew")

        # Tombol "Open Log"
        self.open_log_button = tk.Button(self.root, text="Open Log", command=self.open_log, state=tk.DISABLED)
        self.open_log_button.grid(row=7, column=2, pady=10, sticky="ew")

        # Button to resume the download
        self.resume_button = tk.Button(self.root, text="Resume", command=self.resume_download, state=tk.DISABLED)
        self.resume_button.grid(row=7, column=3, pady=10, sticky="ew")

        # Button to exit the application
        self.exit_button = tk.Button(self.root, text="Exit", command=self.exit_app)
        self.exit_button.grid(row=7, column=4, pady=10, sticky="ew")

    def browse_destination(self):
        destination_folder = filedialog.askdirectory()
        self.destination_entry.delete(0, tk.END)
        self.destination_entry.insert(0, destination_folder)

    def start_download(self):
        # Get the file URL and destination folder
        url = self.url_entry.get()
        destination_folder = self.destination_entry.get()

        # Clear the console
        self.console.delete(1.0, tk.END)

        # Disable the download button
        self.download_button.config(state=tk.DISABLED)
        
        #Disable the Log Button
        self.open_log_button.config(state=tk.DISABLED)

        # Enable the pause button
        self.pause_button.config(state=tk.NORMAL)

        # Reset the pause variable
        self.paused = False

        # Set percentage label to an empty string
        self.percent_label.config(text="")

        # Start a new thread to handle the download
        download_thread = Thread(target=self.download_file, args=(url, destination_folder))
        download_thread.start()

    def pause_download(self):
        # Set the pause variable to True
        self.paused = True

        # Disable the pause button
        self.pause_button.config(state=tk.DISABLED)

        # Enable the resume button
        self.resume_button.config(state=tk.NORMAL)

        # Update status label
        self.status_label.config(text="Download Paused")

    def resume_download(self):
        # Set the pause variable to False
        self.paused = False

        # Disable the resume button
        self.resume_button.config(state=tk.DISABLED)

        # Enable the pause button
        self.pause_button.config(state=tk.NORMAL)

        # Disable the open log button
        self.open_log_button.config(state=tk.DISABLED)

        # Update status label
        self.status_label.config(text="Resuming Download...")

    def open_log(self):
        # Check if the log window is already open
        if not self.log_window_open:
            # Open download log in a new window
            log_window = tk.Toplevel(self.root)
            log_window.title("Download Log")

            # Text widget to display the download log
            log_text = tk.Text(log_window, height=20, width=80)
            log_text.pack()

            # Insert log entries into the text widget
            for log_entry in self.download_log:
                log_text.insert(tk.END, log_entry + "\n")

            # Disable text widget editing
            log_text.config(state=tk.DISABLED)

            # Set the flag to indicate that the log window is open
            self.log_window_open = True

            # Set up a callback to reset the flag when the log window is closed
            log_window.protocol("WM_DELETE_WINDOW", self.on_log_window_close)

    def on_log_window_close(self):
        # Callback when the log window is closed
        self.log_window_open = False

    def report_hook(self, count, block_size, total_size):
        # Calculate download percentage
        percent = min(int(count * block_size * 100 / total_size), 100)
        self.percent_label.config(text=f"{percent}%")

        # Calculate downloaded MB
        downloaded_mb = round(count * block_size / (1024 * 1024), 2)
        total_mb = round(total_size / (1024 * 1024), 2)

        # Calculate download speed
        elapsed_time = datetime.now() - self.start_time
        download_speed = round((count * block_size) / (1024 * 1024 * elapsed_time.total_seconds()), 2)

        # Calculate total file size (only on the first iteration)
        if count == 0:
            self.total_size = total_size

        # Calculate downloaded size
        self.downloaded_size = count * block_size

        # Calculate average download speed
        if elapsed_time.total_seconds() != 0:
            self.average_speed = round(self.downloaded_size / (1024 * 1024 * elapsed_time.total_seconds()), 2)

        # Append progress to console
        progress_info = f"{percent}% downloaded, {downloaded_mb} MB, Speed: {download_speed} MB/s"
        self.console.insert(tk.END, progress_info + "\n")

        # Update log with additional information
        log_entry = f"{datetime.now()} - {percent}% downloaded, {downloaded_mb} MB of {total_mb} MB, Speed: {download_speed} MB/s, Average Speed: {self.average_speed} MB/s"
        self.console.insert(tk.END, log_entry + "\n")
        self.console.see(tk.END)  # Scroll to the end
        self.root.update_idletasks()

        # Check if download is paused
        while self.paused:
            pass

    def download_file(self, url, destination_folder):
        try:
            # Get the file name from the URL
            file_name = url.split("/")[-1]

            # Full path to the destination file
            destination_path = f"{destination_folder}/{file_name}"

            # Update status label
            self.status_label.config(text="Downloading...")

            # Record download start time
            self.start_time = datetime.now()

            # Download the file
            request.urlretrieve(url, destination_path, reporthook=self.report_hook)

            # Record download end time
            end_time = datetime.now()

            # Update status label after download completes
            self.status_label.config(text="Download Complete")

            # Set percentage label to 100% when download is complete
            self.percent_label.config(text="100%")
            self.console.insert(tk.END, "Download Complete\n")

            # Log download information with timestamps
            download_info = f"URL: {url}, Destination: {destination_path}, Start Time: {self.start_time}, End Time: {end_time}, Status: Complete"
            self.download_log.append(download_info)

        except Exception as e:
            # Update status label in case of an error
            self.status_label.config(text=f"Error: {str(e)}")
            self.console.insert(tk.END, f"Error: {str(e)}\n")

            # Log download information with timestamps and error status
            download_info = f"URL: {url}, Destination: {destination_path}, Start Time: {self.start_time}, End Time: {end_time}, Status: Error - {str(e)}"
            self.download_log.append(download_info)

        finally:
            # Enable the download button whether the download is successful or not
            self.download_button.config(state=tk.NORMAL)

            # Disable the pause and resume buttons after download is complete or if an error occurs
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.DISABLED)

            # Enable the "Open Log" button
            self.open_log_button.config(state=tk.NORMAL)

    def exit_app(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileDownloaderApp(root)
    root.mainloop()

