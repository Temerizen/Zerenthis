from .book import generate_book
from .movie import generate_movie
from .podcast import generate_podcast
from .game import generate_game
from .universe import generate_universe
from .lore import generate_lore
from .bundle import generate_bundle

def create_all(topic):
    return generate_bundle(topic)

def create_universe_system(theme):
    universe = generate_universe(theme)
    lore = generate_lore(theme)
    return {
        "universe": universe,
        "lore": lore
    }
