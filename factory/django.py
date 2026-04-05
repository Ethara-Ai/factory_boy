# Copyright: See the LICENSE file.


"""factory_boy extensions for use with the Django framework."""

import functools
import io
import logging
import os
import warnings
from typing import Dict, TypeVar

from django.contrib.auth.hashers import make_password
from django.core import files as django_files
from django.db import IntegrityError

from . import base, declarations, errors

logger = logging.getLogger("factory.generate")


DEFAULT_DB_ALIAS = "default"  # Same as django.db.DEFAULT_DB_ALIAS
T = TypeVar("T")

_LAZY_LOADS: Dict[str, object] = {}


def get_model(app, model):
    """Wrapper around django's get_model."""
    pass


def _lazy_load_get_model():
    """Lazy loading of get_model.

    get_model loads django.conf.settings, which may fail if
    the settings haven't been configured yet.
    """
    pass


class DjangoOptions(base.FactoryOptions):
    def _build_default_options(self):
        pass

    def _get_counter_reference(self):
        pass

    def get_model_class(self):
        pass


class DjangoModelFactory(base.Factory[T]):
    """Factory for Django models.

    This makes sure that the 'sequence' field of created objects is a new id.

    Possible improvement: define a new 'attribute' type, AutoField, which would
    handle those for non-numerical primary keys.
    """

    _options_class = DjangoOptions
    _original_params = None

    class Meta:
        abstract = True  # Optional, but explicit.

    @classmethod
    def _load_model_class(cls, definition):

        pass

    @classmethod
    def _get_manager(cls, model_class):
        pass

    @classmethod
    def _generate(cls, strategy, params):
        # Original params are used in _get_or_create if it cannot build an
        # object initially due to an IntegrityError being raised
        pass

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        """Create an instance of the model through objects.get_or_create."""
        pass

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        pass

    # DEPRECATED. Remove this override with the next major release.
    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        """Save again the instance if creating and at least one hook ran."""
        pass


class Password(declarations.Transformer):
    def __init__(self, password, transform=make_password, **kwargs):
        super().__init__(password, transform=transform, **kwargs)


class FileField(declarations.BaseDeclaration):
    """Helper to fill in django.db.models.FileField from a Factory."""

    DEFAULT_FILENAME = "example.dat"

    def _make_data(self, params):
        """Create data for the field."""
        pass

    def _make_content(self, params):
        pass

    def evaluate(self, instance, step, extra):
        """Fill in the field."""
        pass


class ImageField(FileField):
    DEFAULT_FILENAME = "example.jpg"

    def _make_data(self, params):
        # ImageField (both django's and factory_boy's) require PIL.
        # Try to import it along one of its known installation paths.
        pass


class mute_signals:
    """Temporarily disables and then restores any django signals.

    Args:
        *signals (django.dispatch.dispatcher.Signal): any django signals

    Examples:
        with mute_signals(pre_init):
            user = UserFactory.build()
            ...

        @mute_signals(pre_save, post_save)
        class UserFactory(factory.Factory):
            ...

        @mute_signals(post_save)
        def generate_users():
            UserFactory.create_batch(10)
    """

    def __init__(self, *signals):
        self.signals = signals
        self.paused = {}

    def __enter__(self):
        for signal in self.signals:
            logger.debug("mute_signals: Disabling signal handlers %r", signal.receivers)

            # Note that we're using implementation details of
            # django.signals, since arguments to signal.connect()
            # are lost in signal.receivers
            self.paused[signal] = signal.receivers
            signal.receivers = []

    def __exit__(self, exc_type, exc_value, traceback):
        for signal, receivers in self.paused.items():
            logger.debug("mute_signals: Restoring signal handlers %r", receivers)

            signal.receivers = receivers + signal.receivers
            with signal.lock:
                # Django uses some caching for its signals.
                # Since we're bypassing signal.connect and signal.disconnect,
                # we have to keep messing with django's internals.
                signal.sender_receivers_cache.clear()
        self.paused = {}

    def copy(self):
        pass

    def __call__(self, callable_obj):
        if isinstance(callable_obj, base.FactoryMetaClass):
            # Retrieve __func__, the *actual* callable object.
            callable_obj._create = self.wrap_method(callable_obj._create.__func__)
            callable_obj._generate = self.wrap_method(callable_obj._generate.__func__)
            callable_obj._after_postgeneration = self.wrap_method(
                callable_obj._after_postgeneration.__func__
            )
            return callable_obj

        else:

            @functools.wraps(callable_obj)
            def wrapper(*args, **kwargs):
                # A mute_signals() object is not reentrant; use a copy every time.
                pass

            return wrapper

    def wrap_method(self, method):
        @classmethod
        @functools.wraps(method)
        def wrapped_method(*args, **kwargs):
            pass

        return wrapped_method
