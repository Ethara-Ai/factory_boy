# Copyright: See the LICENSE file.

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from . import base, errors

SESSION_PERSISTENCE_COMMIT = 'commit'
SESSION_PERSISTENCE_FLUSH = 'flush'
VALID_SESSION_PERSISTENCE_TYPES = [
    None,
    SESSION_PERSISTENCE_COMMIT,
    SESSION_PERSISTENCE_FLUSH,
]


class SQLAlchemyOptions(base.FactoryOptions):
    def _check_sqlalchemy_session_persistence(self, meta, value):
        pass

    @staticmethod
    def _check_has_sqlalchemy_session_set(meta, value):
        pass

    def _build_default_options(self):
        pass


class SQLAlchemyModelFactory(base.Factory):
    """Factory for SQLAlchemy models. """

    _options_class = SQLAlchemyOptions
    _original_params = None

    class Meta:
        abstract = True

    @classmethod
    def _generate(cls, strategy, params):
        # Original params are used in _get_or_create if it cannot build an
        # object initially due to an IntegrityError being raised
        pass

    @classmethod
    def _get_or_create(cls, model_class, session, args, kwargs):
        pass

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        pass

    @classmethod
    def _save(cls, model_class, session, args, kwargs):
        pass
