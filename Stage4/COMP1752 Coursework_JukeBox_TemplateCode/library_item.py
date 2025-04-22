class LibraryItem:
    def __init__(self, name, artist, rating=0, play_count=0, image_path=None):
        self.name = name
        self.artist = artist
        self.rating = min(max(0, int(rating)), 5) 
        self.play_count = max(0, int(play_count))  
        self.image_path = str(image_path) if image_path else None

        
    def info(self):
        return f"{self.name} - {self.artist} {self.stars()}"

    def stars(self):
        stars = ""
        for i in range(self.rating):
            stars += "*"
        return stars