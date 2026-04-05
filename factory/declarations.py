# Copyright: See the LICENSE file.


import itertools
import logging
import typing as T

from . import enums, errors, utils

logger = logging.getLogger('factory.generate')


class BaseDeclaration(utils.OrderedBase):
    """A factory declaration.

    Declarations mark an attribute as needing lazy evaluation.
    This allows them to refer to attributes defined by other BaseDeclarations
    in the same factory.
    """

    FACTORY_BUILDER_PHASE = enums.BuilderPhase.ATTRIBUTE_RESOLUTION

    #: Whether this declaration has a special handling for call-time overrides
    #: (e.g. Tranformer).
    #: Overridden values will be passed in the `extra` args.
    CAPTURE_OVERRIDES = False

    #: Whether to unroll the context before evaluating the declaration.
    #: Set to False on declarations that perform their own unrolling.
    UNROLL_CONTEXT_BEFORE_EVALUATION = True

    def __init__(self, **defaults):
        super().__init__()
        self._defaults = defaults or {}

    def unroll_context(self, instance, step, context):
        pass

    def _unwrap_evaluate_pre(self, wrapped, *, instance, step, overrides):
        """Evaluate a wrapped pre-declaration.

        This is especially useful for declarations wrapping another one,
        e.g. Maybe or Transformer.
        """
        pass

    def evaluate_pre(self, instance, step, overrides):
        pass

    def evaluate(self, instance, step, extra):
        """Evaluate this declaration.

        Args:
            instance (builder.Resolver): The object holding currently computed
                attributes
            step: a factory.builder.BuildStep
            extra (dict): additional, call-time added kwargs
                for the step.
        """
        raise NotImplementedError('This is an abstract method')


class OrderedDeclaration(BaseDeclaration):
    """Compatibility"""

    # FIXME(rbarrois)


class LazyFunction(BaseDeclaration):
    """Simplest BaseDeclaration computed by calling the given function.

    Attributes:
        function (function): a function without arguments and
            returning the computed value.
    """

    def __init__(self, function):
        super().__init__()
        self.function = function

    def evaluate(self, instance, step, extra):
        pass


class LazyAttribute(BaseDeclaration):
    """Specific BaseDeclaration computed using a lambda.

    Attributes:
        function (function): a function, expecting the current LazyStub and
            returning the computed value.
    """

    def __init__(self, function):
        super().__init__()
        self.function = function

    def evaluate(self, instance, step, extra):
        pass


class Transformer(BaseDeclaration):
    CAPTURE_OVERRIDES = True
    UNROLL_CONTEXT_BEFORE_EVALUATION = False

    class Force:
        """
        Bypass a transformer's transformation.

        The forced value can be any declaration, and will be evaluated as if it
        had been passed instead of the Transformer declaration.
        """
        def __init__(self, forced_value):
            self.forced_value = forced_value

        def __repr__(self):
            return f'Transformer.Force({repr(self.forced_value)})'

    def __init__(self, default, *, transform):
        super().__init__()
        self.default = default
        self.transform = transform

    def evaluate_pre(self, instance, step, overrides):
        # The call-time value, if present, is set under the "" key.
        pass


class _UNSPECIFIED:
    pass


def deepgetattr(obj, name, default=_UNSPECIFIED):
    """Try to retrieve the given attribute of an object, digging on '.'.

    This is an extended getattr, digging deeper if '.' is found.

    Args:
        obj (object): the object of which an attribute should be read
        name (str): the name of an attribute to look up.
        default (object): the default value to use if the attribute wasn't found

    Returns:
        the attribute pointed to by 'name', splitting on '.'.

    Raises:
        AttributeError: if obj has no 'name' attribute.
    """
    pass


class SelfAttribute(BaseDeclaration):
    """Specific BaseDeclaration copying values from other fields.

    If the field name starts with two dots or more, the lookup will be anchored
    in the related 'parent'.

    Attributes:
        depth (int): the number of steps to go up in the containers chain
        attribute_name (str): the name of the attribute to copy.
        default (object): the default value to use if the attribute doesn't
            exist.
    """

    def __init__(self, attribute_name, default=_UNSPECIFIED):
        super().__init__()
        depth = len(attribute_name) - len(attribute_name.lstrip('.'))
        attribute_name = attribute_name[depth:]

        self.depth = depth
        self.attribute_name = attribute_name
        self.default = default

    def evaluate(self, instance, step, extra):
        pass

    def __repr__(self):
        return '<%s(%r, default=%r)>' % (
            self.__class__.__name__,
            self.attribute_name,
            self.default,
        )


class Iterator(BaseDeclaration):
    """Fill this value using the values returned by an iterator.

    Warning: the iterator should not end !

    Attributes:
        iterator (iterable): the iterator whose value should be used.
        getter (callable or None): a function to parse returned values
    """

    def __init__(self, iterator, cycle=True, getter=None):
        super().__init__()
        self.getter = getter
        self.iterator = None

        if cycle:
            self.iterator_builder = lambda: utils.ResetableIterator(itertools.cycle(iterator))
        else:
            self.iterator_builder = lambda: utils.ResetableIterator(iterator)

    def evaluate(self, instance, step, extra):
        # Begin unrolling as late as possible.
        # This helps with ResetableIterator(MyModel.objects.all())
        pass

    def reset(self):
        """Reset the internal iterator."""
        pass


class Sequence(BaseDeclaration):
    """Specific BaseDeclaration to use for 'sequenced' fields.

    These fields are typically used to generate increasing unique values.

    Attributes:
        function (function): A function, expecting the current sequence counter
            and returning the computed value.
    """
    def __init__(self, function):
        super().__init__()
        self.function = function

    def evaluate(self, instance, step, extra):
        pass


class LazyAttributeSequence(Sequence):
    """Composite of a LazyAttribute and a Sequence.

    Attributes:
        function (function): A function, expecting the current LazyStub and the
            current sequence counter.
        type (function): A function converting an integer into the expected kind
            of counter for the 'function' attribute.
    """
    def evaluate(self, instance, step, extra):
        pass


class ContainerAttribute(BaseDeclaration):
    """Variant of LazyAttribute, also receives the containers of the object.

    Attributes:
        function (function): A function, expecting the current LazyStub and the
            (optional) object having a subfactory containing this attribute.
        strict (bool): Whether evaluating should fail when the containers are
            not passed in (i.e used outside a SubFactory).
    """
    def __init__(self, function, strict=True):
        super().__init__()
        self.function = function
        self.strict = strict

    def evaluate(self, instance, step, extra):
        """Evaluate the current ContainerAttribute.

        Args:
            obj (LazyStub): a lazy stub of the object being constructed, if
                needed.
            containers (list of LazyStub): a list of lazy stubs of factories
                being evaluated in a chain, each item being a future field of
                next one.
        """
        pass


class ParameteredAttribute(BaseDeclaration):
    """Base class for attributes expecting parameters.

    Attributes:
        defaults (dict): Default values for the parameters.
            May be overridden by call-time parameters.
    """

    def evaluate(self, instance, step, extra):
        """Evaluate the current definition and fill its attributes.

        Uses attributes definition in the following order:
        - values defined when defining the ParameteredAttribute
        - additional values defined when instantiating the containing factory

        Args:
            instance (builder.Resolver): The object holding currently computed
                attributes
            step: a factory.builder.BuildStep
            extra (dict): additional, call-time added kwargs
                for the step.
        """
        pass

    def generate(self, step, params):
        """Actually generate the related attribute.

        Args:
            sequence (int): the current sequence number
            obj (LazyStub): the object being constructed
            create (bool): whether the calling factory was in 'create' or
                'build' mode
            params (dict): parameters inherited from init and evaluation-time
                overrides.

        Returns:
            Computed value for the current declaration.
        """
        raise NotImplementedError()


class _FactoryWrapper:
    """Handle a 'factory' arg.

    Such args can be either a Factory subclass, or a fully qualified import
    path for that subclass (e.g 'myapp.factories.MyFactory').
    """
    def __init__(self, factory_or_path):
        self.factory = None
        self.module = self.name = ''
        if isinstance(factory_or_path, type):
            self.factory = factory_or_path
        else:
            if not (isinstance(factory_or_path, str) and '.' in factory_or_path):
                raise ValueError(
                    "A factory= argument must receive either a class "
                    "or the fully qualified path to a Factory subclass; got "
                    "%r instead." % factory_or_path)
            self.module, self.name = factory_or_path.rsplit('.', 1)

    def get(self):
        pass

    def __repr__(self):
        if self.factory is None:
            return f'<_FactoryImport: {self.module}.{self.name}>'
        else:
            return f'<_FactoryImport: {self.factory.__class__}>'


class SubFactory(BaseDeclaration):
    """Base class for attributes based upon a sub-factory.

    Attributes:
        defaults (dict): Overrides to the defaults defined in the wrapped
            factory
        factory (base.Factory): the wrapped factory
    """

    # Whether to align the attribute's sequence counter to the holding
    # factory's sequence counter
    FORCE_SEQUENCE = False
    UNROLL_CONTEXT_BEFORE_EVALUATION = False

    def __init__(self, factory, **kwargs):
        super().__init__(**kwargs)
        self.factory_wrapper = _FactoryWrapper(factory)

    def get_factory(self):
        """Retrieve the wrapped factory.Factory subclass."""
        pass

    def evaluate(self, instance, step, extra):
        """Evaluate the current definition and fill its attributes.

        Args:
            step: a factory.builder.BuildStep
            params (dict): additional, call-time added kwargs
                for the step.
        """
        pass


class Dict(SubFactory):
    """Fill a dict with usual declarations."""

    FORCE_SEQUENCE = True

    def __init__(self, params, dict_factory='factory.DictFactory'):
        super().__init__(dict_factory, **dict(params))


class List(SubFactory):
    """Fill a list with standard declarations."""

    FORCE_SEQUENCE = True

    def __init__(self, params, list_factory='factory.ListFactory'):
        params = {str(i): v for i, v in enumerate(params)}
        super().__init__(list_factory, **params)


# Parameters
# ==========


class Skip:
    def __bool__(self):
        return False


SKIP = Skip()


class Maybe(BaseDeclaration):
    def __init__(self, decider, yes_declaration=SKIP, no_declaration=SKIP):
        super().__init__()

        if enums.get_builder_phase(decider) is None:
            # No builder phase => flat value
            decider = SelfAttribute(decider, default=None)

        self.decider = decider
        self.yes = yes_declaration
        self.no = no_declaration

        phases = {
            'yes_declaration': enums.get_builder_phase(yes_declaration),
            'no_declaration': enums.get_builder_phase(no_declaration),
        }
        used_phases = {phase for phase in phases.values() if phase is not None}

        if len(used_phases) > 1:
            raise TypeError(f"Inconsistent phases for {self!r}: {phases!r}")

        self.FACTORY_BUILDER_PHASE = used_phases.pop() if used_phases else enums.BuilderPhase.ATTRIBUTE_RESOLUTION

    def evaluate_post(self, instance, step, overrides):
        """Handle post-generation declarations"""
        pass

    def evaluate_pre(self, instance, step, overrides):
        pass

    def __repr__(self):
        return f'Maybe({self.decider!r}, yes={self.yes!r}, no={self.no!r})'


class Parameter(utils.OrderedBase):
    """A complex parameter, to be used in a Factory.Params section.

    Must implement:
    - A "compute" function, performing the actual declaration override
    - Optionally, a get_revdeps() function (to compute other parameters it may alter)
    """

    def as_declarations(self, field_name, declarations):
        """Compute the overrides for this parameter.

        Args:
        - field_name (str): the field this parameter is installed at
        - declarations (dict): the global factory declarations

        Returns:
            dict: the declarations to override
        """
        raise NotImplementedError()

    def get_revdeps(self, parameters):
        """Retrieve the list of other parameters modified by this one."""
        pass


class SimpleParameter(Parameter):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def as_declarations(self, field_name, declarations):
        pass

    @classmethod
    def wrap(cls, value):
        pass


class Trait(Parameter):
    """The simplest complex parameter, it enables a bunch of new declarations based on a boolean flag."""
    def __init__(self, **overrides):
        super().__init__()
        self.overrides = overrides

    def as_declarations(self, field_name, declarations):
        pass

    def get_revdeps(self, parameters):
        """This might alter fields it's injecting."""
        pass

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join('%s=%r' % t for t in self.overrides.items())
        )


# Post-generation
# ===============


class PostGenerationContext(T.NamedTuple):
    value_provided: bool
    value: T.Any
    extra: T.Dict[str, T.Any]


class PostGenerationDeclaration(BaseDeclaration):
    """Declarations to be called once the model object has been generated."""

    FACTORY_BUILDER_PHASE = enums.BuilderPhase.POST_INSTANTIATION

    def evaluate_post(self, instance, step, overrides):
        pass

    def call(self, instance, step, context):  # pragma: no cover
        """Call this hook; no return value is expected.

        Args:
            instance (object): the newly generated object
            step (bool): whether the object was 'built' or 'created'
            context: a declarations.PostGenerationContext containing values
                extracted from the containing factory's declaration
        """
        raise NotImplementedError()


class PostGeneration(PostGenerationDeclaration):
    """Calls a given function once the object has been generated."""
    def __init__(self, function):
        super().__init__()
        self.function = function

    def call(self, instance, step, context):
        pass


class RelatedFactory(PostGenerationDeclaration):
    """Calls a factory once the object has been generated.

    Attributes:
        factory (Factory): the factory to call
        defaults (dict): extra declarations for calling the related factory
        name (str): the name to use to refer to the generated object when
            calling the related factory
    """

    UNROLL_CONTEXT_BEFORE_EVALUATION = False

    def __init__(self, factory, factory_related_name='', **defaults):
        super().__init__()

        self.name = factory_related_name
        self.defaults = defaults
        self.factory_wrapper = _FactoryWrapper(factory)

    def get_factory(self):
        """Retrieve the wrapped factory.Factory subclass."""
        pass

    def call(self, instance, step, context):
        pass


class RelatedFactoryList(RelatedFactory):
    """Calls a factory 'size' times once the object has been generated.

    Attributes:
        factory (Factory): the factory to call "size-times"
        defaults (dict): extra declarations for calling the related factory
        factory_related_name (str): the name to use to refer to the generated
            object when calling the related factory
        size (int|lambda): the number of times 'factory' is called, ultimately
            returning a list of 'factory' objects w/ size 'size'.
    """

    def __init__(self, factory, factory_related_name='', size=2, **defaults):
        self.size = size
        super().__init__(factory, factory_related_name, **defaults)

    def call(self, instance, step, context):
        pass


class NotProvided:
    pass


class PostGenerationMethodCall(PostGenerationDeclaration):
    """Calls a method of the generated object.

    Attributes:
        method_name (str): the method to call
        method_args (list): arguments to pass to the method
        method_kwargs (dict): keyword arguments to pass to the method

    Example:
        class UserFactory(factory.Factory):
            ...
            password = factory.PostGenerationMethodCall('set_pass', password='')
    """
    def __init__(self, method_name, *args, **kwargs):
        super().__init__()
        if len(args) > 1:
            raise errors.InvalidDeclarationError(
                "A PostGenerationMethodCall can only handle 1 positional argument; "
                "please provide other parameters through keyword arguments."
            )
        self.method_name = method_name
        self.method_arg = args[0] if args else NotProvided
        self.method_kwargs = kwargs

    def call(self, instance, step, context):
        pass
