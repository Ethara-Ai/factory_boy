"""Build factory instances."""

import collections

from . import enums, errors, utils

DeclarationWithContext = collections.namedtuple(
    'DeclarationWithContext',
    ['name', 'declaration', 'context'],
)


class DeclarationSet:
    """A set of declarations, including the recursive parameters.

    Attributes:
        declarations (dict(name => declaration)): the top-level declarations
        contexts (dict(name => dict(subfield => value))): the nested parameters related
            to a given top-level declaration

    This object behaves similarly to a dict mapping a top-level declaration name to a
    DeclarationWithContext, containing field name, declaration object and extra context.
    """

    def __init__(self, initial=None):
        self.declarations = {}
        self.contexts = collections.defaultdict(dict)
        self.update(initial or {})

    @classmethod
    def split(cls, entry):
        """Split a declaration name into a (declaration, subpath) tuple.

        Examples:
        >>> DeclarationSet.split('foo__bar')
        ('foo', 'bar')
        >>> DeclarationSet.split('foo')
        ('foo', None)
        >>> DeclarationSet.split('foo__bar__baz')
        ('foo', 'bar__baz')
        """
        pass

    @classmethod
    def join(cls, root, subkey):
        """Rebuild a full declaration name from its components.

        for every string x, we have `join(split(x)) == x`.
        """
        pass

    def copy(self):
        pass

    def update(self, values):
        """Add new declarations to this set/

        Args:
            values (dict(name, declaration)): the declarations to ingest.
        """
        pass

    def filter(self, entries):
        """Filter a set of declarations: keep only those related to this object.

        This will keep:
        - Declarations that 'override' the current ones
        - Declarations that are parameters to current ones
        """
        pass

    def sorted(self):
        pass

    def __contains__(self, key):
        return key in self.declarations

    def __getitem__(self, key):
        return DeclarationWithContext(
            name=key,
            declaration=self.declarations[key],
            context=self.contexts[key],
        )

    def __iter__(self):
        return iter(self.declarations)

    def values(self):
        """Retrieve the list of declarations, with their context."""
        pass

    def _items(self):
        """Extract a list of (key, value) pairs, suitable for our __init__."""
        pass

    def as_dict(self):
        """Return a dict() suitable for our __init__."""
        pass

    def __repr__(self):
        return '<DeclarationSet: %r>' % self.as_dict()


def _captures_overrides(declaration_with_context):
    pass


def parse_declarations(decls, base_pre=None, base_post=None):
    pass


class BuildStep:
    def __init__(self, builder, sequence, parent_step=None):
        self.builder = builder
        self.sequence = sequence
        self.attributes = {}
        self.parent_step = parent_step
        self.stub = None

    def resolve(self, declarations):
        pass

    @property
    def chain(self):
        pass

    def recurse(self, factory, declarations, force_sequence=None):
        pass

    def __repr__(self):
        return f"<BuildStep for {self.builder!r}>"


class StepBuilder:
    """A factory instantiation step.

    Attributes:
    - parent: the parent StepBuilder, or None for the root step
    - extras: the passed-in kwargs for this branch
    - factory: the factory class being built
    - strategy: the strategy to use
    """
    def __init__(self, factory_meta, extras, strategy):
        self.factory_meta = factory_meta
        self.strategy = strategy
        self.extras = extras
        self.force_init_sequence = extras.pop('__sequence', None)

    def build(self, parent_step=None, force_sequence=None):
        """Build a factory instance."""
        pass

    def recurse(self, factory_meta, extras):
        """Recurse into a sub-factory call."""
        pass

    def __repr__(self):
        return f"<StepBuilder({self.factory_meta!r}, strategy={self.strategy!r})>"


class Resolver:
    """Resolve a set of declarations.

    Attributes are set at instantiation time, values are computed lazily.

    Attributes:
        __initialized (bool): whether this object's __init__ as run. If set,
            setting any attribute will be prevented.
        __declarations (dict): maps attribute name to their declaration
        __values (dict): maps attribute name to computed value
        __pending (str list): names of the attributes whose value is being
            computed. This allows to detect cyclic lazy attribute definition.
        __step (BuildStep): the BuildStep related to this resolver.
            This allows to have the value of a field depend on the value of
            another field
    """

    __initialized = False

    def __init__(self, declarations, step, sequence):
        self.__declarations = declarations
        self.__step = step

        self.__values = {}
        self.__pending = []

        self.__initialized = True

    @property
    def factory_parent(self):
        pass

    def __repr__(self):
        return '<Resolver for %r>' % self.__step

    def __getattr__(self, name):
        """Retrieve an attribute's value.

        This will compute it if needed, unless it is already on the list of
        attributes being computed.
        """
        if name in self.__pending:
            raise errors.CyclicDefinitionError(
                "Cyclic lazy attribute definition for %r; cycle found in %r." %
                (name, self.__pending))
        elif name in self.__values:
            return self.__values[name]
        elif name in self.__declarations:
            declaration = self.__declarations[name]
            value = declaration.declaration
            if enums.get_builder_phase(value) == enums.BuilderPhase.ATTRIBUTE_RESOLUTION:
                self.__pending.append(name)
                try:
                    value = value.evaluate_pre(
                        instance=self,
                        step=self.__step,
                        overrides=declaration.context,
                    )
                finally:
                    last = self.__pending.pop()
                assert name == last

            self.__values[name] = value
            return value
        else:
            raise AttributeError(
                "The parameter %r is unknown. Evaluated attributes are %r, "
                "definitions are %r." % (name, self.__values, self.__declarations))

    def __setattr__(self, name, value):
        """Prevent setting attributes once __init__ is done."""
        if not self.__initialized:
            return super().__setattr__(name, value)
        else:
            raise AttributeError('Setting of object attributes is not allowed')
