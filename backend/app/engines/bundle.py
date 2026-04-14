from .book import generate_book
from .movie import generate_movie
from .podcast import generate_podcast
from .game import generate_game

def generate_bundle(topic):
    return {
        "book": generate_book(topic),
        "movie": generate_movie(topic),
        "podcast": generate_podcast(topic),
        "game": generate_game(topic)
    }

