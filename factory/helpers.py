# Copyright: See the LICENSE file.


"""Simple wrappers around Factory class definition."""

import contextlib
import logging

from . import base, declarations


@contextlib.contextmanager
def debug(logger='factory', stream=None):
    pass


def make_factory(klass, **kwargs):
    """Create a new, simple factory for the given class."""
    pass


def build(klass, **kwargs):
    """Create a factory for the given class, and build an instance."""
    pass


def build_batch(klass, size, **kwargs):
    """Create a factory for the given class, and build a batch of instances."""
    pass


def create(klass, **kwargs):
    """Create a factory for the given class, and create an instance."""
    pass


def create_batch(klass, size, **kwargs):
    """Create a factory for the given class, and create a batch of instances."""
    pass


def stub(klass, **kwargs):
    """Create a factory for the given class, and stub an instance."""
    pass


def stub_batch(klass, size, **kwargs):
    """Create a factory for the given class, and stub a batch of instances."""
    pass


def generate(klass, strategy, **kwargs):
    """Create a factory for the given class, and generate an instance."""
    pass


def generate_batch(klass, strategy, size, **kwargs):
    """Create a factory for the given class, and generate instances."""
    pass


def simple_generate(klass, create, **kwargs):
    """Create a factory for the given class, and simple_generate an instance."""
    pass


def simple_generate_batch(klass, create, size, **kwargs):
    """Create a factory for the given class, and simple_generate instances."""
    pass


def lazy_attribute(func):
    pass


def iterator(func):
    """Turn a generator function into an iterator attribute."""
    pass


def sequence(func):
    pass


def lazy_attribute_sequence(func):
    pass


def container_attribute(func):
    pass


def post_generation(fun):
    pass
