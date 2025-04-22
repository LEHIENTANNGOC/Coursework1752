import tkinter as tk
from tkinter import ttk, messagebox
import track_library


class JukeBoxApp:
    """
    Main application class for the JukeBox music player.
    Provides a GUI interface to browse, search, and manage music tracks.
    Features include track searching, playlist management, and track editing.
    """

    def __init__(self, window):
        """
        Initialize the JukeBox application with main window and setup UI components

        Args:
            window: The main Tkinter root window
        """
        self.window = window
        self.playlist_items = []  # Stores current playlist tracks as (track_id, track) tuples
        self.library = track_library.library  # Reference to the track library dictionary

        self._configure_window()
        self._setup_tabs()
        self._initialize_ui_components()

    def _configure_window(self):
        """Configure main window settings including title, size and background"""
        self.window.title("JukeBox")
        self.window.geometry("1200x600")  # Width x Height
        self.window.configure(bg="gray")  # Set background color

    def _setup_tabs(self):
        """
        Setup notebook tabs for the application:
        - Main tab: Contains search functionality and track library
        - Playlists tab: For creating and managing playlists
        """
        self.tab_control = ttk.Notebook(self.window)
        self.main_tab = ttk.Frame(self.tab_control)
        self.playlist_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.main_tab, text="Main")
        self.tab_control.add(self.playlist_tab, text="Playlists")
        self.tab_control.pack(expand=1, fill="both")

    def _initialize_ui_components(self):
        """
        Initialize all UI components for both tabs.
        Creates search interface, track display areas, and playlist interface.
        """
        self._setup_search_ui()
        self._setup_track_display()
        self._setup_playlist_ui()

    def _setup_search_ui(self):
        """
        Create search interface components including entry field and buttons.
        Search functionality allows looking up tracks by ID.
        """
        search_frame = ttk.Frame(self.main_tab)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        # Search label and entry
        ttk.Label(search_frame, text="Search").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()  # Variable to hold search text
        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=30
        )
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # Search and clear buttons
        ttk.Button(
            search_frame,
            text="Search",
            command=self._perform_search
        ).pack(side=tk.LEFT)

        ttk.Button(
            search_frame,
            text="Clear",
            command=self._clear_search
        ).pack(side=tk.LEFT, padx=5)

    def _setup_track_display(self):
        """
        Setup the track display areas:
        - Left side: Shows all available tracks in the library
        - Right side: Displays search results or default message
        """
        self.main_display_frame = ttk.Frame(self.main_tab)
        self.main_display_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for all tracks
        self.all_tracks_frame = ttk.LabelFrame(self.main_display_frame)
        self.all_tracks_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.all_tracks_frame.pack_propagate(False)  # Prevents frame from shrinking to fit content

        # Right frame for search results
        self.search_results_frame = ttk.LabelFrame(self.main_display_frame)
        self.search_results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.search_results_frame.pack_propagate(False)  # Prevents frame from shrinking to fit content

        # Initialize displays
        self._display_all_tracks()  # Show all tracks in the library
        self._display_default_track()  # Show default message in search area

    def _setup_playlist_ui(self):
        """
        Setup the playlist tab interface with play button and scrollable track list.
        Allows for managing a custom playlist of tracks.
        """
        playlist_container = ttk.Frame(self.playlist_tab)
        playlist_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Play All button
        play_button_frame = ttk.Frame(playlist_container)
        play_button_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(
            play_button_frame,
            text="Play All",
            command=self._play_all_tracks,
            width=15
        ).pack(side=tk.LEFT, padx=10)

        # Current playlist setup with scrollbar for larger playlists
        left_frame = ttk.LabelFrame(playlist_container, text="Current Playlist")
        left_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create scrollable container for playlist items
        scroll_container = ttk.Frame(left_frame)
        scroll_container.pack(fill="both", expand=True)

        playlist_canvas = tk.Canvas(scroll_container)
        playlist_scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=playlist_canvas.yview)

        self.playlist_scrollable_frame = ttk.Frame(playlist_canvas)
        # Configure canvas scroll region when frame size changes
        self.playlist_scrollable_frame.bind(
            "<Configure>",
            lambda e: playlist_canvas.configure(
                scrollregion=playlist_canvas.bbox("all")
            )
        )

        playlist_canvas.create_window((0, 0), window=self.playlist_scrollable_frame, anchor="nw")
        playlist_canvas.configure(yscrollcommand=playlist_scrollbar.set)

        playlist_canvas.pack(side="left", fill="both", expand=True)
        playlist_scrollbar.pack(side="right", fill="y")

        # Initialize playlist display
        self._update_playlist_display()

    def _play_all_tracks(self):
        """
        Play all tracks in playlist and increment play count for each track.
        Shows a confirmation dialog with list of played tracks.
        """
        if not self.playlist_items:
            messagebox.showinfo("Empty Playlist", "There are no tracks in the playlist to play.")
            return

        # Prepare list of track names to display
        track_names = []

        # Iterate through each track in playlist
        for track_id, track in self.playlist_items:
            # Increment play count in track library
            track_library.increment_play_count(track_id)

            # Get track info for display
            track_name = track_library.get_name(track_id)
            track_artist = track_library.get_artist(track_id)
            track_playcount = track_library.get_play_count((track_id))
            track_names.append(f"{track_name} - {track_artist} - play count: {track_playcount}")

        # Update UI to reflect play count changes
        self._update_playlist_display()
        self._display_all_tracks()

        # Show notification with played tracks
        messagebox.showinfo(
            "Playing All",
            f"Now playing {len(self.playlist_items)} tracks:\n")

    def _display_all_tracks(self):
        """
        Display all tracks in the left frame with scrollable interface.
        Shows track ID, name, artist, and star rating for each track.
        """
        self._clear_frame(self.all_tracks_frame)  # Remove existing content

        # Create scrollable container
        container = ttk.Frame(self.all_tracks_frame)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add each track to the display
        for track_id, track in self.library.items():
            track_frame = ttk.Frame(scrollable_frame)
            track_frame.pack(fill="x", padx=10, pady=5)

            # Show track info with ID, name, artist and star rating
            info = f"{track_id}: {track.name} - {track.artist} ({track.stars()})"
            ttk.Label(track_frame, text=info, font=("Arial", 12)).pack(side="left", padx=10)

    def _display_default_track(self):
        """
        Display default message in search results frame when no search performed.
        Provides user guidance on how to use the search feature.
        """
        ttk.Label(
            self.search_results_frame,
            text="Enter a search term to see results here",
            font=("Arial", 12)
        ).pack(pady=20)

    def normalize_track_key(self, key):
        """
        Convert track key to standardized 2-digit format (e.g., "1" -> "01")

        Args:
            key (str): The track ID to normalize

        Returns:
            str: Normalized 2-digit ID or None if conversion fails
        """
        try:
            return f"{int(key):02d}"  # Format as 2-digit number with leading zero if needed
        except ValueError:
            return None  # Return None if key can't be converted to int

    def _perform_search(self):
        """
        Execute search based on track ID and display results.
        Supports both normalized and original key formats.
        """
        search_term = self.search_var.get().strip()
        normalized_key = self.normalize_track_key(search_term)

        self._clear_frame(self.search_results_frame)  # Clear previous results

        # Try first with the normalized key if available
        if normalized_key and normalized_key in self.library:
            track = self.library[normalized_key]
            self._create_track_display(self.search_results_frame, normalized_key, track)
            return
        # Then try with the original search term
        elif search_term in self.library:
            track = self.library[search_term]
            self._create_track_display(self.search_results_frame, search_term, track)
            return
        # If neither works, show not found message
        else:
            ttk.Label(
                self.search_results_frame,
                text=f"No matching tracks found",
                font=("Arial", 12)
            ).pack(pady=20)
            return

    def _create_track_display(self, parent_frame, track_id, track):
        """
        Create a detailed track display with information and action buttons.

        Args:
            parent_frame: The frame where track info will be displayed
            track_id: The ID of the track to display
            track: The track object containing track details
        """
        # Track info display section
        info = f"{track.name} - {track.artist}"
        ttk.Label(parent_frame, text=info, font=("Arial", 12, "bold")).pack(side="top", anchor="w", padx=10)

        # Play count and rating info
        play_info = f"Play count: {track.play_count} | Rating: {track.rating}"
        ttk.Label(parent_frame, text=play_info, font=("Arial", 10)).pack(side="top", anchor="w", padx=10)

        # Action buttons section
        buttons_frame = ttk.Frame(parent_frame)
        buttons_frame.pack(side="top", anchor="w", padx=10, pady=5)

        # Play button - plays the track and increments play count
        ttk.Button(
            buttons_frame,
            text="Play",
            command=lambda id=track_id: self._play_track(id)
        ).pack(side="left", padx=5)

        # Add to Playlist button - adds track to current playlist
        ttk.Button(
            buttons_frame,
            text="Add to Playlist",
            command=lambda id=track_id: self._add_to_playlist(id)
        ).pack(side="left", padx=5)

        # Edit button - opens dialog to edit track details
        ttk.Button(
            buttons_frame,
            text="Edit",
            command=lambda id=track_id: self._edit_track(id)
        ).pack(side="left", padx=5)

    def _play_track(self, track_id):
        """
        Play the selected track and increment its play count.
        Shows a confirmation dialog with updated play count.

        Args:
            track_id: The ID of the track to play
        """
        track_name = track_library.get_name(track_id)
        track_artist = track_library.get_artist(track_id)

        if track_name and track_artist:
            # Increment play count in library
            track_library.increment_play_count(track_id)
            updated_play_count = track_library.get_play_count(track_id)

            # Show confirmation dialog
            messagebox.showinfo(
                "Playing",
                f"Now playing: {track_name} by {track_artist}\nPlay count: {updated_play_count}"
            )

            # Refresh search results to show updated play count
            self._perform_search()

    def _add_to_playlist(self, track_id):
        """
        Add track to playlist if it's not already present.
        Shows confirmation message when track is added.

        Args:
            track_id: The ID of the track to add to playlist
        """
        track = self.library.get(track_id)
        if not track:
            return  # Track not found in library

        # Check if track is already in playlist to prevent duplicates
        if track_id not in [item[0] for item in self.playlist_items]:
            self.playlist_items.append((track_id, track))
            self._update_playlist_display()  # Refresh playlist UI
            messagebox.showinfo("Added", f"Added '{track.name}' to playlist")

    def _update_playlist_display(self):
        """
        Update playlist display with current items.
        Clears existing display and recreates it with current playlist tracks.
        """
        self._clear_frame(self.playlist_scrollable_frame)

        # Create display for each playlist item
        for track_id, track in self.playlist_items:
            self._create_playlist_item_display(track_id, track)

    def _create_playlist_item_display(self, track_id, track):
        """
        Create display for a single playlist item with remove button.

        Args:
            track_id: The ID of the track to display
            track: The track object containing track details
        """
        item_frame = ttk.Frame(self.playlist_scrollable_frame)
        item_frame.pack(fill="x", padx=10, pady=5)

        # Get current play count and rating from library
        track_play_count = track_library.get_play_count(track_id)
        track_rating = track_library.get_rating(track_id)

        # Display track basic info
        info = f"{track_id}: {track.name} - {track.artist} - Rating {track.rating} "
        ttk.Label(item_frame, text=info, font=("Arial", 11)).pack(side="left", padx=10)

        # Display track play count and rating
        play_info = f"Play count: {track_play_count} | Rating: {track_rating}"
        ttk.Label(item_frame, text=play_info, font=("Arial", 12)).pack(side="left", padx=10)

        # Add remove button
        ttk.Button(
            item_frame,
            text="Remove",
            command=lambda id=track_id: self._remove_from_playlist(id)
        ).pack(side="right", padx=5)

    def _remove_from_playlist(self, track_id):
        """
        Remove specified track from the playlist.

        Args:
            track_id: The ID of the track to remove
        """
        # Filter out the track with matching ID
        self.playlist_items = [item for item in self.playlist_items if item[0] != track_id]
        self._update_playlist_display()  # Refresh playlist UI

    def _edit_track(self, track_id):
        """
        Open a dialog window to edit track details.

        Args:
            track_id: The ID of the track to edit
        """
        track = self.library.get(track_id)
        if not track:
            return  # Track not found in library

        # Create edit dialog window
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Track")
        edit_window.geometry("400x300")

        # Create and pack widgets for editing
        name_var, artist_var, rating_var = self._create_edit_widgets(edit_window, track)

        # Save button
        ttk.Button(
            edit_window,
            text="Save Changes",
            command=lambda: self._save_track_changes(
                track_id, track, name_var, artist_var, rating_var, edit_window
            )
        ).pack(pady=10)

    def _create_edit_widgets(self, parent, track):
        """
        Create widgets for track editing dialog including entry fields.

        Args:
            parent: The parent window/frame for the widgets
            track: The track object to edit

        Returns:
            tuple: (name_var, artist_var, rating_var) StringVar objects
            containing the editable values
        """
        # Track name field
        ttk.Label(parent, text="Track Name:").pack(pady=(10, 0))
        name_var = tk.StringVar(value=track.name)
        ttk.Entry(parent, textvariable=name_var, width=40).pack(pady=5)

        # Artist field
        ttk.Label(parent, text="Artist:").pack(pady=(10, 0))
        artist_var = tk.StringVar(value=track.artist)
        ttk.Entry(parent, textvariable=artist_var, width=40).pack(pady=5)

        # Rating field (0-5)
        ttk.Label(parent, text="Rating (0-5):").pack(pady=(10, 0))
        rating_var = tk.StringVar(value=str(track.rating))
        ttk.Entry(parent, textvariable=rating_var, width=40).pack(pady=5)

        return name_var, artist_var, rating_var

    def _save_track_changes(self, track_id, track, name_var, artist_var, rating_var, window):
        """
        Save changes made to track details and update display.

        Args:
            track_id: The ID of the track being edited
            track: The track object to update
            name_var: StringVar containing the new name
            artist_var: StringVar containing the new artist
            rating_var: StringVar containing the new rating
            window: The edit dialog window to close after saving
        """
        try:
            # Update track properties
            track.name = name_var.get()
            track.artist = artist_var.get()

            # Validate and update rating (must be 0-5)
            rating = int(rating_var.get())
            if 0 <= rating <= 5:
                track.rating = rating
                track_library.set_rating(track_id, rating)
            else:
                raise ValueError("Rating must be between 0 and 5")

            # Refresh UI displays
            self._display_all_tracks()
            self._perform_search()
            self._update_playlist_display()

            # Close edit window and show confirmation
            window.destroy()
            messagebox.showinfo("Success", "Track updated successfully")
        except ValueError as e:
            # Show error if input validation fails
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    def _clear_search(self):
        """
        Reset search field and clear search results display.
        Restores default message in search results area.
        """
        self.search_var.set("")  # Clear search text
        self._clear_frame(self.search_results_frame)  # Clear results
        self._display_default_track()  # Show default message

    def _clear_frame(self, frame):
        """
        Clear all widgets from the specified frame.

        Args:
            frame: The frame whose contents should be removed
        """
        for widget in frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = JukeBoxApp(root)
    root.mainloop()  # Start the Tkinter event loop