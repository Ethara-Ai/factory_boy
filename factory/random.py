import random

import faker.generator

randgen = random.Random()

randgen.state_set = False


def get_random_state():
    """Retrieve the state of factory.fuzzy's random generator."""
    pass


def set_random_state(state):
    """Force-set the state of factory.fuzzy's random generator."""
    pass


def reseed_random(seed):
    """Reseed factory.fuzzy's random generator."""
    pass
