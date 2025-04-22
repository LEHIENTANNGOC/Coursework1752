import tkinter as tk
from tkinter import ttk


class JukeBoxLayout:
    """Main class for the JukeBox UI layout"""

    def __init__(self, window):
        # Store the main window reference
        self.window = window

        # Configure the main window
        self.window.title("JukeBox Layout")
        self.window.geometry("1200x600")  # Set default window size

        # Create tab control for multiple views
        self.tab_control = ttk.Notebook(self.window)
        self._create_main_tab()  # Initialize the main browsing tab
        self._create_playlist_tab()  # Initialize the playlist management tab

        # Display the tab control with expand and fill options
        self.tab_control.pack(expand=1, fill="both")

    def _create_main_tab(self):
        """Create layout for the Main tab with search and track display areas"""
        main_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(main_tab, text="Main")

        # Search frame - contains search input and action buttons
        search_frame = ttk.Frame(main_tab)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        ttk.Entry(search_frame, width=30).pack(side=tk.LEFT, padx=5)  # Search input field
        ttk.Button(search_frame, text="Search").pack(side=tk.LEFT)  # Search activation button
        ttk.Button(search_frame, text="Clear").pack(side=tk.LEFT, padx=5)  # Clear search button

        # Main display frame - contains two side-by-side panels
        display_frame = ttk.Frame(main_tab)
        display_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - All Tracks listing
        all_tracks_frame = ttk.LabelFrame(display_frame, text="All Tracks")
        all_tracks_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._create_scrollable_area(all_tracks_frame)  # Add scrolling capability

        # Right panel - Search Results display
        search_results_frame = ttk.LabelFrame(display_frame, text="Search Results")
        search_results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._create_scrollable_area(search_results_frame)  # Add scrolling capability

    def _create_playlist_tab(self):
        """Create layout for the Playlist tab with controls and track listing"""
        playlist_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(playlist_tab, text="Playlists")

        # Control buttons for playlist management
        control_frame = ttk.Frame(playlist_tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(control_frame, text="Play All", width=15).pack(side=tk.LEFT)  # Play all tracks in playlist

        # Playlist tracks display
        playlist_frame = ttk.LabelFrame(playlist_tab, text="Current Playlist")
        playlist_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self._create_scrollable_area(playlist_frame)  # Add scrolling capability

    def _create_scrollable_area(self, parent):
        """Create a scrollable frame area within the given parent widget

        This method creates a canvas with scrollbar to allow scrolling when content
        exceeds the available space.
        """
        # Create container frame for canvas and scrollbar
        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True)

        # Create canvas (scrollable area) and scrollbar
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        # Create frame inside canvas to hold content
        scrollable_frame = ttk.Frame(canvas)
        # Configure canvas scroll region when frame size changes
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Add frame to canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        # Link scrollbar to canvas
        canvas.configure(yscrollcommand=scrollbar.set)

        # Position canvas and scrollbar in container
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


if __name__ == "__main__":
    # Initialize main application window
    root = tk.Tk()
    app = JukeBoxLayout(root)
    # Start the Tkinter event loop
    root.mainloop()