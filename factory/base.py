# Copyright: See the LICENSE file.


import collections
import logging
import warnings
from typing import Generic, List, Type, TypeVar

from . import builder, declarations, enums, errors, utils

logger = logging.getLogger('factory.generate')

T = TypeVar('T')

# Factory metaclasses


def get_factory_bases(bases):
    """Retrieve all FactoryMetaClass-derived bases from a list."""
    pass


def resolve_attribute(name, bases, default=None):
    """Find the first definition of an attribute according to MRO order."""
    pass


class FactoryMetaClass(type):
    """Factory metaclass for handling ordered declarations."""

    def __call__(cls, **kwargs):
        """Override the default Factory() syntax to call the default strategy.

        Returns an instance of the associated class.
        """

        if cls._meta.strategy == enums.BUILD_STRATEGY:
            return cls.build(**kwargs)
        elif cls._meta.strategy == enums.CREATE_STRATEGY:
            return cls.create(**kwargs)
        elif cls._meta.strategy == enums.STUB_STRATEGY:
            return cls.stub(**kwargs)
        else:
            raise errors.UnknownStrategy('Unknown Meta.strategy: {}'.format(
                cls._meta.strategy))

    def __new__(mcs, class_name, bases, attrs):
        """Record attributes as a pattern for later instance construction.

        This is called when a new Factory subclass is defined; it will collect
        attribute declaration from the class definition.

        Args:
            class_name (str): the name of the class being created
            bases (list of class): the parents of the class being created
            attrs (str => obj dict): the attributes as defined in the class
                definition

        Returns:
            A new class
        """
        parent_factories = get_factory_bases(bases)
        if parent_factories:
            base_factory = parent_factories[0]
        else:
            base_factory = None

        attrs_meta = attrs.pop('Meta', None)
        attrs_params = attrs.pop('Params', None)

        base_meta = resolve_attribute('_meta', bases)
        options_class = resolve_attribute('_options_class', bases, FactoryOptions)

        meta = options_class()
        attrs['_meta'] = meta

        new_class = super().__new__(
            mcs, class_name, bases, attrs)

        meta.contribute_to_class(
            new_class,
            meta=attrs_meta,
            base_meta=base_meta,
            base_factory=base_factory,
            params=attrs_params,
        )

        return new_class

    def __str__(cls):
        if cls._meta.abstract:
            return '<%s (abstract)>' % cls.__name__
        else:
            return f'<{cls.__name__} for {cls._meta.model}>'


class BaseMeta:
    abstract = True
    strategy = enums.CREATE_STRATEGY


class OptionDefault:
    """The default for an option.

    Attributes:
        name: str, the name of the option ('class Meta' attribute)
        value: object, the default value for the option
        inherit: bool, whether to inherit the value from the parent factory's `class Meta`
            when no value is provided
        checker: callable or None, an optional function used to detect invalid option
            values at declaration time
    """
    def __init__(self, name, value, inherit=False, checker=None):
        self.name = name
        self.value = value
        self.inherit = inherit
        self.checker = checker

    def apply(self, meta, base_meta):
        pass

    def __str__(self):
        return '%s(%r, %r, inherit=%r)' % (
            self.__class__.__name__,
            self.name, self.value, self.inherit)


class FactoryOptions:
    def __init__(self):
        self.factory = None
        self.base_factory = None
        self.base_declarations = {}
        self.parameters = {}
        self.parameters_dependencies = {}
        self.pre_declarations = builder.DeclarationSet()
        self.post_declarations = builder.DeclarationSet()

        self._counter = None
        self.counter_reference = None

    @property
    def declarations(self):
        pass

    def _build_default_options(self):
        """"Provide the default value for all allowed fields.

        Custom FactoryOptions classes should override this method
        to update() its return value.
        """
        pass

    def _fill_from_meta(self, meta, base_meta):
        # Exclude private/protected fields from the meta
        pass

    def contribute_to_class(self, factory, meta=None, base_meta=None, base_factory=None, params=None):

        pass

    def _get_counter_reference(self):
        """Identify which factory should be used for a shared counter."""
        pass

    def _initialize_counter(self):
        """Initialize our counter pointer.

        If we're the top-level factory, instantiate a new counter
        Otherwise, point to the top-level factory's counter.
        """
        pass

    def next_sequence(self):
        """Retrieve a new sequence ID.

        This will call, in order:
        - next_sequence from the base factory, if provided
        - _setup_next_sequence, if this is the 'toplevel' factory and the
            sequence counter wasn't initialized yet; then increase it.
        """
        pass

    def reset_sequence(self, value=None, force=False):
        pass

    def prepare_arguments(self, attributes):
        """Convert an attributes dict to a (args, kwargs) tuple."""
        pass

    def instantiate(self, step, args, kwargs):
        pass

    def use_postgeneration_results(self, step, instance, results):
        pass

    def _is_declaration(self, name, value):
        """Determines if a class attribute is a field value declaration.

        Based on the name and value of the class attribute, return ``True`` if
        it looks like a declaration of a default field value, ``False`` if it
        is private (name starts with '_') or a classmethod or staticmethod.

        """
        pass

    def _check_parameter_dependencies(self, parameters):
        """Find out in what order parameters should be called."""
        pass

    def get_model_class(self):
        """Extension point for loading model classes.

        This can be overridden in framework-specific subclasses to hook into
        existing model repositories, for instance.
        """
        pass

    def __str__(self):
        return "<%s for %s>" % (self.__class__.__name__, self.factory.__name__)

    def __repr__(self):
        return str(self)


# Factory base classes


class _Counter:
    """Simple, naive counter.

    Attributes:
        for_class (obj): the class this counter related to
        seq (int): the next value
    """

    def __init__(self, seq):
        self.seq = seq

    def next(self):
        pass

    def reset(self, next_value=0):
        pass


class BaseFactory(Generic[T]):
    """Factory base support for sequences, attributes and stubs."""

    # Backwards compatibility
    UnknownStrategy = errors.UnknownStrategy
    UnsupportedStrategy = errors.UnsupportedStrategy

    def __new__(cls, *args, **kwargs):
        """Would be called if trying to instantiate the class."""
        raise errors.FactoryError('You cannot instantiate BaseFactory')

    _meta = FactoryOptions()

    # ID to use for the next 'declarations.Sequence' attribute.
    _counter = None

    @classmethod
    def reset_sequence(cls, value=None, force=False):
        """Reset the sequence counter.

        Args:
            value (int or None): the new 'next' sequence value; if None,
                recompute the next value from _setup_next_sequence().
            force (bool): whether to force-reset parent sequence counters
                in a factory inheritance chain.
        """
        pass

    @classmethod
    def _setup_next_sequence(cls):
        """Set up an initial sequence value for Sequence attributes.

        Returns:
            int: the first available ID to use for instances of this factory.
        """
        pass

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        """Extension point for custom kwargs adjustment."""
        pass

    @classmethod
    def _generate(cls, strategy, params):
        """generate the object.

        Args:
            params (dict): attributes to use for generating the object
            strategy: the strategy to use
        """
        pass

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        """Hook called after post-generation declarations have been handled.

        Args:
            instance (object): the generated object
            create (bool): whether the strategy was 'build' or 'create'
            results (dict or None): result of post-generation declarations
        """
        pass

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        """Actually build an instance of the model_class.

        Customization point, will be called once the full set of args and kwargs
        has been computed.

        Args:
            model_class (type): the class for which an instance should be
                built
            args (tuple): arguments to use when building the class
            kwargs (dict): keyword arguments to use when building the class
        """
        pass

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Actually create an instance of the model_class.

        Customization point, will be called once the full set of args and kwargs
        has been computed.

        Args:
            model_class (type): the class for which an instance should be
                created
            args (tuple): arguments to use when creating the class
            kwargs (dict): keyword arguments to use when creating the class
        """
        pass

    @classmethod
    def build(cls, **kwargs) -> T:
        """Build an instance of the associated class, with overridden attrs.

        The instance will not be saved and persisted to any datastore.
        """
        pass

    @classmethod
    def build_batch(cls, size: int, **kwargs) -> List[T]:
        """Build a batch of instances of the given class, with overridden attrs.

        The instances will not be saved and persisted to any datastore.

        Args:
            size (int): the number of instances to build

        Returns:
            object list: the built instances
        """
        pass

    @classmethod
    def create(cls, **kwargs) -> T:
        """Create an instance of the associated class, with overridden attrs.

        The instance will be saved and persisted in the appropriate datastore.
        """
        pass

    @classmethod
    def create_batch(cls, size: int, **kwargs) -> List[T]:
        """Create a batch of instances of the given class, with overridden attrs.

        The instances will be saved and persisted in the appropriate datastore.

        Args:
            size (int): the number of instances to create

        Returns:
            object list: the created instances
        """
        pass

    @classmethod
    def stub(cls, **kwargs):
        """Retrieve a stub of the associated class, with overridden attrs.

        This will return an object whose attributes are those defined in this
        factory's declarations or in the extra kwargs.
        """
        pass

    @classmethod
    def stub_batch(cls, size, **kwargs):
        """Stub a batch of instances of the given class, with overridden attrs.

        Args:
            size (int): the number of instances to stub

        Returns:
            object list: the stubbed instances
        """
        pass

    @classmethod
    def generate(cls, strategy, **kwargs):
        """Generate a new instance.

        The instance will be created with the given strategy (one of
        BUILD_STRATEGY, CREATE_STRATEGY, STUB_STRATEGY).

        Args:
            strategy (str): the strategy to use for generating the instance.

        Returns:
            object: the generated instance
        """
        pass

    @classmethod
    def generate_batch(cls, strategy, size, **kwargs):
        """Generate a batch of instances.

        The instances will be created with the given strategy (one of
        BUILD_STRATEGY, CREATE_STRATEGY, STUB_STRATEGY).

        Args:
            strategy (str): the strategy to use for generating the instance.
            size (int): the number of instances to generate

        Returns:
            object list: the generated instances
        """
        pass

    @classmethod
    def simple_generate(cls, create, **kwargs):
        """Generate a new instance.

        The instance will be either 'built' or 'created'.

        Args:
            create (bool): whether to 'build' or 'create' the instance.

        Returns:
            object: the generated instance
        """
        pass

    @classmethod
    def simple_generate_batch(cls, create, size, **kwargs):
        """Generate a batch of instances.

        These instances will be either 'built' or 'created'.

        Args:
            size (int): the number of instances to generate
            create (bool): whether to 'build' or 'create' the instances.

        Returns:
            object list: the generated instances
        """
        pass


class Factory(BaseFactory[T], metaclass=FactoryMetaClass):
    """Factory base with build and create support.

    This class has the ability to support multiple ORMs by using custom creation
    functions.
    """

    # Backwards compatibility
    AssociatedClassError: Type[Exception]

    class Meta(BaseMeta):
        pass


# Add the association after metaclass execution.
# Otherwise, AssociatedClassError would be detected as a declaration.
Factory.AssociatedClassError = errors.AssociatedClassError


class StubObject:
    """A generic container."""
    def __init__(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)


class StubFactory(Factory):

    class Meta:
        strategy = enums.STUB_STRATEGY
        model = StubObject

    @classmethod
    def build(cls, **kwargs):
        pass

    @classmethod
    def create(cls, **kwargs):
        raise errors.UnsupportedStrategy()


class BaseDictFactory(Factory):
    """Factory for dictionary-like classes."""
    class Meta:
        abstract = True

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        pass

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        pass


class DictFactory(BaseDictFactory):
    class Meta:
        model = dict


class BaseListFactory(Factory):
    """Factory for list-like classes."""
    class Meta:
        abstract = True

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        pass

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        pass


class ListFactory(BaseListFactory):
    class Meta:
        model = list


def use_strategy(new_strategy):
    """Force the use of a different strategy.

    This is an alternative to setting default_strategy in the class definition.
    """
    pass
