"""Random helper aliases built on top of `secrets.SystemRandom`."""

from secrets import SystemRandom

__all__ = (
    "random",
    "random_bool",
    "random_choice",
    "random_int",
    "random_ratio",
    "random_uniform",
    "random_sample",
    "random_seed",
)

random = SystemRandom()

random_choice = random.choice
random_int = random.randint
random_ratio = random.random
random_uniform = random.uniform
random_sample = random.sample
random_seed = random.seed


def random_bool():
    """Return a random boolean value."""
    return random.choice([True, False])
