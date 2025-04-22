import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import csv
from library_item import LibraryItem
import track_library


class JukeBoxApp:
    def __init__(self, window):
        self.window = window
        self.playlist_items = []  # List to store tracks added to playlist

        self._configure_window()
        self._setup_tabs()
        self._load_tracks_from_csv("tracks_data.csv")
        self._initialize_ui_components()

    def _configure_window(self):
        # Set up the main window properties
        self.window.title("JukeBox")
        self.window.geometry("1200x600")
        self.window.configure(bg="gray")

    def _setup_tabs(self):
        # Create main and playlist tabs
        self.tab_control = ttk.Notebook(self.window)
        self.main_tab = ttk.Frame(self.tab_control)
        self.playlist_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.main_tab, text="Main")
        self.tab_control.add(self.playlist_tab, text="Playlists")
        self.tab_control.pack(expand=1, fill="both")

    def _initialize_ui_components(self):
        # Initialize all UI components
        self._setup_search_ui()
        self._setup_track_display()
        self._setup_playlist_ui()

    def _load_tracks_from_csv(self, filename):
        # Load tracks from CSV file into the track_library
        try:
            with open(filename, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    item = LibraryItem(
                        name=row.get('Title'),
                        artist=row.get('Artist'),
                        rating=(row.get('Rating', 0)),
                        play_count=row.get('Play Count', 0),
                        image_path=row.get('Image Path')
                    )
                    if 'ID' in row:
                        track_library.library[row['ID']] = item

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tracks: {str(e)}")

    def _setup_search_ui(self):
        # Create search interface with search field and filter options
        search_frame = ttk.Frame(self.main_tab)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=30
        )
        self.search_entry.pack(side=tk.LEFT, padx=5)

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

        # Search filter options
        search_options_frame = ttk.Frame(search_frame)
        search_options_frame.pack(side=tk.LEFT, padx=10)

        ttk.Label(search_options_frame, text="Search by:").pack(side=tk.LEFT)

        self.search_option = tk.StringVar(value="ALL")
        ttk.Combobox(
            search_options_frame,
            textvariable=self.search_option,
            values=["ALL", "Tracks", "Artists"],
            state="readonly",
            width=10
        ).pack(side=tk.LEFT, padx=5)

    def _setup_track_display(self):
        # Create display areas for tracks and search results
        self.main_display_frame = ttk.Frame(self.main_tab)
        self.main_display_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel for all tracks
        self.all_tracks_frame = ttk.LabelFrame(self.main_display_frame)
        self.all_tracks_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.all_tracks_frame.pack_propagate(False)

        # Right panel for search results
        self.search_results_frame = ttk.LabelFrame(self.main_display_frame)
        self.search_results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.search_results_frame.pack_propagate(False)

        self._display_all_tracks()
        self._display_default_track()

    def _setup_playlist_ui(self):
        # Create playlist interface and controls
        playlist_container = ttk.Frame(self.playlist_tab)
        playlist_container.pack(fill="both", expand=True, padx=10, pady=10)

        playlist_frame = ttk.LabelFrame(playlist_container, text="Current Playlist")
        playlist_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Play All button
        play_button_frame = ttk.Frame(playlist_frame)
        play_button_frame.pack(fill="x", pady=(5, 10))

        ttk.Button(
            play_button_frame,
            text="Play All",
            command=self._play_all_tracks,
            width=15
        ).pack(side=tk.LEFT, padx=10)

        # Scrollable playlist container
        scroll_container = ttk.Frame(playlist_frame)
        scroll_container.pack(fill="both", expand=True)

        playlist_canvas = tk.Canvas(scroll_container)
        playlist_scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=playlist_canvas.yview)

        self.playlist_scrollable_frame = ttk.Frame(playlist_canvas)
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

        self._update_playlist_display()

    def _play_all_tracks(self):
        # Play all tracks in playlist and update play counts
        if not self.playlist_items:
            messagebox.showinfo("Empty Playlist", "There are no tracks in the playlist to play.")
            return

        track_names = []

        for track_id, _ in self.playlist_items:
            # Increment play count
            track_library.increment_play_count(track_id)

            # Get track info for display
            track_name = track_library.get_name(track_id)
            track_artist = track_library.get_artist(track_id)
            track_names.append(f"{track_name} - {track_artist}")

        # Update UI
        self._update_playlist_display()
        self._display_all_tracks()

        messagebox.showinfo(
            "Playing All",
            f"Now playing {len(self.playlist_items)} tracks")

    def _display_all_tracks(self):
        # Show all tracks in library with scrollbar
        self._clear_frame(self.all_tracks_frame)

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

        # Add each track to display
        for track_id, track in track_library.library.items():
            self._create_track_display(scrollable_frame, track_id, track, show_buttons=False)

    def _display_default_track(self):
        # Show default message in search results area
        ttk.Label(
            self.search_results_frame,
            text="Enter a search term to see results here",
            font=("Arial", 12)
        ).pack(pady=20)

    def _perform_search(self):
        # Execute search and display results
        search_term = self.search_var.get().strip().lower()
        search_type = self.search_option.get()

        self._clear_frame(self.search_results_frame)

        results = self._filter_tracks(search_term, search_type)

        if not results:
            ttk.Label(
                self.search_results_frame,
                text="No matching tracks found",
                font=("Arial", 12)
            ).pack(pady=20)
            return

        for track_id, track in results.items():
            self._create_track_display(
                self.search_results_frame,
                track_id,
                track,
                show_buttons=True
            )

    def _filter_tracks(self, search_term, search_type):
        # Filter tracks based on search criteria
        results = {}

        for track_id, track in track_library.library.items():
            match = False

            if search_type in ["ALL", "Tracks"] and search_term in track.name.lower():
                match = True

            if not match and search_type in ["ALL", "Artists"] and search_term in track.artist.lower():
                match = True

            if match:
                results[track_id] = track

        return results

    def _create_track_display(self, parent_frame, track_id, track, show_buttons=False):
        # Create visual display for a track
        track_frame = ttk.Frame(parent_frame)
        track_frame.pack(fill="x", padx=10, pady=5)

        self._display_track_image(track_frame, track)

        track_name = track_library.get_name(track_id) or track.name
        track_artist = track_library.get_artist(track_id) or track.artist

        if show_buttons:
            self._create_detailed_track_display(track_frame, track_id, track_name, track_artist)
        else:
            self._create_basic_track_display(track_frame, track_name, track_artist)

    def _display_track_image(self, parent_frame, track):
        # Show track album art or placeholder
        if hasattr(track, 'image_path') and track.image_path and os.path.exists(track.image_path):
            try:
                img = Image.open(track.image_path).resize((80, 80), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                image_label = ttk.Label(parent_frame, image=img_tk)
                image_label.image = img_tk
                image_label.pack(side="left", padx=10)
            except Exception as e:
                print(f"Error loading image {track.image_path}: {e}")
                ttk.Label(parent_frame, text="No Image", font=("Arial", 10)).pack(side="left", padx=10)
        else:
            ttk.Label(parent_frame, text="No Image", font=("Arial", 10)).pack(side="left", padx=10)

    def _create_basic_track_display(self, parent_frame, track_name, track_artist):
        # Simple track display with name and artist
        info = f"{track_name} - {track_artist}"
        ttk.Label(parent_frame, text=info, font=("Arial", 12)).pack(side="left", padx=10)

    def _create_detailed_track_display(self, parent_frame, track_id, track_name, track_artist):
        # Detailed track display with play count, rating and buttons
        info = f"{track_name} - {track_artist}"
        ttk.Label(parent_frame, text=info, font=("Arial", 12, "bold")).pack(side="top", anchor="w", padx=10)

        track_play_count = track_library.get_play_count(track_id)
        track_rating = track_library.get_rating(track_id)

        play_info = f"Play count: {track_play_count} | Rating: {track_rating}"
        ttk.Label(parent_frame, text=play_info, font=("Arial", 10)).pack(side="top", anchor="w", padx=10)

        buttons_frame = ttk.Frame(parent_frame)
        buttons_frame.pack(side="top", anchor="w", padx=10, pady=5)

        # Action buttons for track
        ttk.Button(
            buttons_frame,
            text="Play",
            command=lambda id=track_id: self._play_track(id)
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons_frame,
            text="Add to Playlist",
            command=lambda id=track_id: self._add_to_playlist(id)
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons_frame,
            text="Edit",
            command=lambda id=track_id: self._edit_track(id)
        ).pack(side="left", padx=5)

    def _play_track(self, track_id):
        # Play selected track and update its play count
        track_name = track_library.get_name(track_id)
        track_artist = track_library.get_artist(track_id)

        if track_name and track_artist:
            track_library.increment_play_count(track_id)
            updated_play_count = track_library.get_play_count(track_id)

            messagebox.showinfo(
                "Playing",
                f"Now playing: {track_name} by {track_artist}\nPlay count: {updated_play_count}"
            )
            self._display_all_tracks()
            self._perform_search()

    def _add_to_playlist(self, track_id):
        # Add track to playlist if not already present
        track = track_library.library.get(track_id)
        if not track:
            return

        # Check if track already exists in playlist
        if track_id not in [item[0] for item in self.playlist_items]:
            self.playlist_items.append((track_id, track))
            self._update_playlist_display()

    def _update_playlist_display(self):
        # Refresh playlist UI with current tracks
        self._clear_frame(self.playlist_scrollable_frame)

        for track_id, track in self.playlist_items:
            self._create_playlist_item_display(track_id, track)

    def _create_playlist_item_display(self, track_id, track):
        # Create UI for a single playlist item
        item_frame = ttk.Frame(self.playlist_scrollable_frame)
        item_frame.pack(fill="x", padx=10, pady=5, ipady=5)

        self._display_track_image(item_frame, track)

        track_name = track_library.get_name(track_id) or track.name
        track_artist = track_library.get_artist(track_id) or track.artist

        track_play_count = track_library.get_play_count(track_id)
        track_rating = track_library.get_rating(track_id)

        info = f"{track_name} - {track_artist}"
        ttk.Label(item_frame, text=info, font=("Arial", 12)).pack(side="left", padx=10)
        play_info = f"Play count: {track_play_count} | Rating: {track_rating}"
        ttk.Label(item_frame, text=play_info, font=("Arial", 12)).pack(side="left", padx=10)

        # Remove button
        ttk.Button(
            item_frame,
            text="Remove",
            command=lambda id=track_id: self._remove_from_playlist(id)
        ).pack(side="right", padx=5)

    def _remove_from_playlist(self, track_id):
        # Remove track from playlist using list comprehension
        self.playlist_items = [item for item in self.playlist_items if item[0] != track_id]
        self._update_playlist_display()

    def _edit_track(self, track_id):
        # Open dialog to edit track details
        track = track_library.library.get(track_id)
        if not track:
            return

        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Track")
        edit_window.geometry("400x300")

        # Create edit form
        name_var, artist_var, rating_var = self._create_edit_widgets(edit_window, track)

        ttk.Button(
            edit_window,
            text="Save Changes",
            command=lambda: self._save_track_changes(
                track_id, track, name_var, artist_var, rating_var, edit_window
            )
        ).pack(pady=10)

    def _create_edit_widgets(self, parent, track):
        # Create form fields for track editing
        ttk.Label(parent, text="Track Name:").pack(pady=(10, 0))
        name_var = tk.StringVar(value=track.name)
        ttk.Entry(parent, textvariable=name_var, width=40).pack(pady=5)

        ttk.Label(parent, text="Artist:").pack(pady=(10, 0))
        artist_var = tk.StringVar(value=track.artist)
        ttk.Entry(parent, textvariable=artist_var, width=40).pack(pady=5)

        ttk.Label(parent, text="Rating (0-5):").pack(pady=(10, 0))
        rating_var = tk.StringVar(value=str(track.rating))
        ttk.Entry(parent, textvariable=rating_var, width=40).pack(pady=5)

        return name_var, artist_var, rating_var

    def _save_track_changes(self, track_id, track, name_var, artist_var, rating_var, window):
        # Save edited track data
        try:
            track.name = name_var.get()
            track.artist = artist_var.get()
            track.rating = min(max(0, int(rating_var.get())), 5)

            # Update the track in library
            if track_id in track_library.library:
                track_library.library[track_id] = track

            self._display_all_tracks()
            self._update_playlist_display()

            window.destroy()
            messagebox.showinfo("Success", "Track updated successfully")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for rating and play count")

    def _clear_search(self):
        # Clear search field and results
        self.search_var.set("")
        self._clear_frame(self.search_results_frame)
        self._display_default_track()

    def _clear_frame(self, frame):
        # Remove all widgets from a frame
        for widget in frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = JukeBoxApp(root)
    root.mainloop()