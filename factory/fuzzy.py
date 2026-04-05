# Copyright: See the LICENSE file.


"""Additional declarations for "fuzzy" attribute definitions."""


import datetime
import decimal
import string
import warnings

from . import declarations, random

random_seed_warning = (
    "Setting a specific random seed for {} can still have varying results "
    "unless you also set a specific end date. For details and potential solutions "
    "see https://github.com/FactoryBoy/factory_boy/issues/331"
)


class BaseFuzzyAttribute(declarations.BaseDeclaration):
    """Base class for fuzzy attributes.

    Custom fuzzers should override the `fuzz()` method.
    """

    def fuzz(self):  # pragma: no cover
        raise NotImplementedError()

    def evaluate(self, instance, step, extra):
        pass


class FuzzyAttribute(BaseFuzzyAttribute):
    """Similar to LazyAttribute, but yields random values.

    Attributes:
        function (callable): function taking no parameters and returning a
            random value.
    """

    def __init__(self, fuzzer):
        super().__init__()
        self.fuzzer = fuzzer

    def fuzz(self):
        pass


class FuzzyText(BaseFuzzyAttribute):
    """Random string with a given prefix.

    Generates a random string of the given length from chosen chars.
    If a prefix or a suffix are supplied, they will be prepended / appended
    to the generated string.

    Args:
        prefix (text): An optional prefix to prepend to the random string
        length (int): the length of the random part
        suffix (text): An optional suffix to append to the random string
        chars (str list): the chars to choose from

    Useful for generating unique attributes where the exact value is
    not important.
    """

    def __init__(self, prefix='', length=12, suffix='', chars=string.ascii_letters):
        super().__init__()
        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.chars = tuple(chars)  # Unroll iterators

    def fuzz(self):
        pass


class FuzzyChoice(BaseFuzzyAttribute):
    """Handles fuzzy choice of an attribute.

    Args:
        choices (iterable): An iterable yielding options; will only be unrolled
            on the first call.
        getter (callable or None): a function to parse returned values
    """

    def __init__(self, choices, getter=None):
        self.choices = None
        self.choices_generator = choices
        self.getter = getter
        super().__init__()

    def fuzz(self):
        pass


class FuzzyInteger(BaseFuzzyAttribute):
    """Random integer within a given range."""

    def __init__(self, low, high=None, step=1):
        if high is None:
            high = low
            low = 0

        self.low = low
        self.high = high
        self.step = step

        super().__init__()

    def fuzz(self):
        pass


class FuzzyDecimal(BaseFuzzyAttribute):
    """Random decimal within a given range."""

    def __init__(self, low, high=None, precision=2):
        if high is None:
            high = low
            low = 0.0

        self.low = low
        self.high = high
        self.precision = precision

        super().__init__()

    def fuzz(self):
        pass


class FuzzyFloat(BaseFuzzyAttribute):
    """Random float within a given range."""

    def __init__(self, low, high=None, precision=15):
        if high is None:
            high = low
            low = 0

        self.low = low
        self.high = high
        self.precision = precision

        super().__init__()

    def fuzz(self):
        pass


class FuzzyDate(BaseFuzzyAttribute):
    """Random date within a given date range."""

    def __init__(self, start_date, end_date=None):
        super().__init__()
        if end_date is None:
            if random.randgen.state_set:
                cls_name = self.__class__.__name__
                warnings.warn(random_seed_warning.format(cls_name), stacklevel=2)
            end_date = datetime.date.today()

        if start_date > end_date:
            raise ValueError(
                "FuzzyDate boundaries should have start <= end; got %r > %r."
                % (start_date, end_date))

        self.start_date = start_date.toordinal()
        self.end_date = end_date.toordinal()

    def fuzz(self):
        pass


class BaseFuzzyDateTime(BaseFuzzyAttribute):
    """Base class for fuzzy datetime-related attributes.

    Provides fuzz() computation, forcing year/month/day/hour/...
    """

    def _check_bounds(self, start_dt, end_dt):
        pass

    def _now(self):
        raise NotImplementedError()

    def __init__(self, start_dt, end_dt=None,
                 force_year=None, force_month=None, force_day=None,
                 force_hour=None, force_minute=None, force_second=None,
                 force_microsecond=None):
        super().__init__()

        if end_dt is None:
            if random.randgen.state_set:
                cls_name = self.__class__.__name__
                warnings.warn(random_seed_warning.format(cls_name), stacklevel=2)
            end_dt = self._now()

        self._check_bounds(start_dt, end_dt)

        self.start_dt = start_dt
        self.end_dt = end_dt
        self.force_year = force_year
        self.force_month = force_month
        self.force_day = force_day
        self.force_hour = force_hour
        self.force_minute = force_minute
        self.force_second = force_second
        self.force_microsecond = force_microsecond

    def fuzz(self):
        pass


class FuzzyNaiveDateTime(BaseFuzzyDateTime):
    """Random naive datetime within a given range.

    If no upper bound is given, will default to datetime.datetime.now().
    """

    def _now(self):
        pass

    def _check_bounds(self, start_dt, end_dt):
        pass


class FuzzyDateTime(BaseFuzzyDateTime):
    """Random timezone-aware datetime within a given range.

    If no upper bound is given, will default to datetime.datetime.now()
    If no timezone is given, will default to utc.
    """

    def _now(self):
        pass

    def _check_bounds(self, start_dt, end_dt):
        pass
