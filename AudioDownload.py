import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import os
import yt_dlp

class  AudioDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Downloader")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        self.downloads_dir = os.path.join(os.path.expanduser("~"), "AudioDownloads")

        if not os.path.exists(self.downloads_dir):
            os.makedirs(self.downloads_dir)

        self.download_thread = None
        self.stop_download = False

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_label = ttk.Label(main_frame, text="Audio Downloader", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        ttk.Label(main_frame, text="Enter YouTube URL:").grid(row=1, column=0, sticky=tk.W, pady=5)

        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.url_entry.bind('<Return>', lambda e: self.add_url())

        self.create_context_menu(self.url_entry)

        self.add_btn = ttk.Button(main_frame, text="Add URL", command=self.add_url)
        self.add_btn.grid(row=2, column=2, padx=5)

        ttk.Label(main_frame, text="URLs to download:").grid(row=3, column=0, sticky=tk.W, pady=5)

        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        self.url_list = tk.Listbox(list_frame, height=8, width=70)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.url_list.yview)
        self.url_list.configure(yscrollcommand=scrollbar.set)

        self.url_list.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.create_context_menu(self.url_list)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=5)

        self.remove_btn = ttk.Button(btn_frame, text="Remove Selected", command=self.remove_selected_url)
        self.remove_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(btn_frame, text="Clear All", command=self.clear_urls)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        ttk.Label(main_frame, text="Download folder:").grid(row=6, column=0, sticky=tk.W, pady=5)

        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.dir_btn = ttk.Button(dir_frame, text="Select Folder", command=self.select_download_directory)
        self.dir_btn.pack(side=tk.LEFT)

        self.dir_label = ttk.Label(dir_frame, text=self.downloads_dir)
        self.dir_label.pack(side=tk.LEFT, padx=10)

        ttk.Label(main_frame, text="Progress:").grid(row=8, column=0, sticky=tk.W, pady=5)

        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.status_label = ttk.Label(main_frame, text="Ready to download")
        self.status_label.grid(row=10, column=0, columnspan=3, pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=11, column=0, columnspan=3, pady=10)

        self.download_btn = ttk.Button(button_frame, text="Start Download", command=self.start_download)
        self.download_btn.pack(side=tk.LEFT, padx=10)

        self.cancel_btn = ttk.Button(button_frame, text="Cancel Download", command=self.cancel_download, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=10)
        ttk.Label(main_frame, text="Download Log:").grid(row=12, column=0, sticky=tk.W, pady=5)

        self.log_area = scrolledtext.ScrolledText(main_frame, height=10, width=70)
        self.log_area.grid(row=13, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(13, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

    def create_context_menu(self, widget):
        """Create a right-click context menu for the given widget"""
        context_menu = tk.Menu(widget, tearoff=0)
        context_menu.add_command(label="Cut", command=lambda: widget.event_generate('<<Cut>>'))
        context_menu.add_command(label="Copy", command=lambda: widget.event_generate('<<Copy>>'))
        context_menu.add_command(label="Paste", command=lambda: widget.event_generate('<<Paste>>'))

        if isinstance(widget, tk.Listbox):
            widget.bind("<Button-3>", lambda e: context_menu.tk_popup(e.x_root, e.y_root))
        else:
            widget.bind("<Button-3>", lambda e: context_menu.tk_popup(e.x_root, e.y_root))

    def add_url(self):
        url = self.url_entry.get().strip()
        if url:
            if url not in self.url_list.get(0, tk.END):
                self.url_list.insert(tk.END, url)
                self.url_entry.delete(0, tk.END)
                self.log_message(f"Added URL: {url}")
            else:
                messagebox.showwarning("Duplicate URL", "This URL is already in the list.")
        else:
            messagebox.showwarning("Empty URL", "Please enter a URL.")

    def remove_selected_url(self):
        selected = self.url_list.curselection()
        if selected:
            self.url_list.delete(selected)

    def clear_urls(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all URLs?"):
            self.url_list.delete(0, tk.END)

    def select_download_directory(self):
        directory = filedialog.askdirectory(initialdir=self.downloads_dir)
        if directory:
            self.downloads_dir = directory
            self.dir_label.config(text=directory)

    def start_download(self):
        if self.url_list.size() == 0:
            messagebox.showwarning("No URLs", "Please add at least one URL to download.")
            return

        self.download_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress_bar['value'] = 0

        urls = self.url_list.get(0, tk.END)
        self.stop_download = False

        self.download_thread = threading.Thread(target=self.download_files, args=(urls,))
        self.download_thread.daemon = True
        self.download_thread.start()

        self.update_status("Download started...")

    def download_files(self, urls):
        total = len(urls)
        for i, url in enumerate(urls):
            if self.stop_download:
                break

            try:
                self.log_message(f"Downloading: {url}")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': os.path.join(self.downloads_dir, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                self.log_message(f"Successfully downloaded: {url}")
            except Exception as e:
                self.log_message(f"Error downloading {url}: {str(e)}")

            progress = int((i + 1) / total * 100)
            self.update_progress(progress)

        self.download_complete()

    def update_progress(self, value):
        def update():
            self.progress_bar['value'] = value
        self.root.after(0, update)

    def download_complete(self):
        def update():
            self.download_btn.config(state=tk.NORMAL)
            self.cancel_btn.config(state=tk.DISABLED)
            self.update_status("Download completed Look in Your Directory")
        self.root.after(0, update)

    def cancel_download(self):
        self.stop_download = True
        self.update_status("Download cancelled")
        self.log_message("Download cancelled by user")
        self.download_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)

    def log_message(self, message):
        def update_log():
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
        self.root.after(0, update_log)

    def update_status(self, message):
        def update_label():
            self.status_label.config(text=message)
        self.root.after(0, update_label)

def main():

    try:
        import yt_dlp
    except ImportError:
        print("Error: yt-dlp is not installed.")
        print("Please install it using: pip install yt-dlp")
        return
 
    root = tk.Tk()
    app = AudioDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
