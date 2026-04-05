# Copyright: See the LICENSE file.


"""factory_boy extensions for use with the mogo library (pymongo wrapper)."""


from . import base


class MogoFactory(base.Factory):
    """Factory for mogo objects."""
    class Meta:
        abstract = True

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        pass

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        pass
