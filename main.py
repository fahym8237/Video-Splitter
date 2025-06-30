import tkinter as tk
from tkinter import filedialog, messagebox
import ffmpeg
import imageio_ffmpeg
import os

# GUI App Class
class VideoSplitterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Video Splitter")
        self.master.geometry("600x400")
        self.splits = []

        # Input video file
        self.input_path = tk.StringVar()

        # UI Components
        self.create_widgets()

    def create_widgets(self):
        # Browse video
        tk.Label(self.master, text="Input Video:").pack(anchor="w", padx=10, pady=5)
        input_frame = tk.Frame(self.master)
        input_frame.pack(fill="x", padx=10)
        tk.Entry(input_frame, textvariable=self.input_path, width=60).pack(side="left", fill="x", expand=True)
        tk.Button(input_frame, text="Browse", command=self.browse_file).pack(side="right")

        # Split list display
        self.split_listbox = tk.Listbox(self.master, height=8)
        self.split_listbox.pack(fill="both", padx=10, pady=(10, 5), expand=True)

        # Start / End entry fields
        split_frame = tk.Frame(self.master)
        split_frame.pack(padx=10)

        tk.Label(split_frame, text="Start (hh:mm:ss):").grid(row=0, column=0, padx=5, pady=5)
        self.start_entry = tk.Entry(split_frame)
        self.start_entry.grid(row=0, column=1)

        tk.Label(split_frame, text="End (hh:mm:ss):").grid(row=0, column=2, padx=5)
        self.end_entry = tk.Entry(split_frame)
        self.end_entry.grid(row=0, column=3)

        tk.Button(split_frame, text="Add Split", command=self.add_split).grid(row=0, column=4, padx=10)

        # Start and Exit buttons
        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Start Splitting", command=self.start_splitting, bg="#4CAF50", fg="white", width=20).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Exit", command=self.master.quit, bg="#f44336", fg="white", width=10).pack(side="right", padx=10)

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
        if path:
            self.input_path.set(path)

    def add_split(self):
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        if not start or not end:
            messagebox.showerror("Error", "Please enter both start and end time.")
            return
        label = f"{start} to {end}"
        self.splits.append((start, end))
        self.split_listbox.insert(tk.END, label)
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)

    def start_splitting(self):
        video = self.input_path.get()
        if not video or not os.path.exists(video):
            messagebox.showerror("Error", "Please select a valid video file.")
            return
        if not self.splits:
            messagebox.showerror("Error", "No split periods defined.")
            return

        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

        base = os.path.splitext(os.path.basename(video))[0]
        output_dir = os.path.dirname(video)

        for i, (start, end) in enumerate(self.splits, start=1):
            output_path = os.path.join(output_dir, f"{base}_part{i}.mp4")
            input_stream = ffmpeg.input(video)
            output_stream = (
                ffmpeg
                .output(
                    input_stream,
                    output_path,
                    ss=start,
                    to=end,
                    vcodec='libx264',
                    acodec='aac',
                    preset='fast',
                    crf=23
                )
                .overwrite_output()
            )
            try:
                ffmpeg.run(output_stream, cmd=ffmpeg_path)
                self.split_listbox.insert(tk.END, f"✅ Created {output_path}")
            except ffmpeg.Error as e:
                messagebox.showerror("FFmpeg Error", f"Failed to create {output_path}\n{e.stderr.decode()}")

        messagebox.showinfo("Done", "All splits completed successfully.")

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoSplitterApp(root)
    root.mainloop()
