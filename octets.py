"""
Painless bytes.
"""
import decimal
import six
import sys
import re

_LESS_THAN_PY35 = sys.version_info < (3, 5)

_numeric_types = six.integer_types + (float, decimal.Decimal)

_BYTES_FORMAT = re.compile("%(\([^)diouxXeEfFgGcrs%]+\))?b")


class octets(object):
    """
    A friendly and consistent bytes wrapper.

    Iterating over an instance yields single-character byte strings:

    >>> list(octets(b'abc'))
    [b'a', b'b', b'c']

    So does indexing an instance:

    >>> b'abc'[0]
    b'a'

    Trying to call :py:class:`str` or :py:class:`unicode` on an
    instance raises a :py:exc:`TypeError`.  Percent formatting works
    on all supported Pythons.
    """

    def __init__(self, object=b'', encoding=None, errors=None):
        """
        Create an :py:class:`octets` instance from the given object.

        A numeric type instance (:py:class:`int`, :py:class:`float`,
        :py:class:`Decimal`) is converted to its base-10
        representation and encoded to ``ascii``.

        >>> octets(10)
        octets(b'10')

        A text type instance (:py:class:`str` on Python 3 and
        :py:class:`unicode` on Python 2) is encoded to bytes per
        ``encoding``:

        >>> octets('a, encoding='utf-16be')
        octets(b'\x00a')

        A :py:class:`bytes` instance is not converted at all.

        >>> octets(b'a')
        octets(b'a')

        :param object: The object to wrap in bytes.
        :param encoding: (optional) The encoding to use when
            ``object`` is a text type instance.  Ignored otherwise.
        :param encoding: (optional) The error strategy to use when
            encoding an ``object`` that is a text type instance.
            Ignored otherwise.
        """
        if isinstance(object, _numeric_types):
            self._bytes = str(object).encode('ascii')
        elif isinstance(object, six.text_type):
            if encoding is None:
                raise TypeError("string argument without an encoding")
            if errors:
                self._bytes = object.encode(encoding, errors)
            else:
                self._bytes = object.encode(encoding)
        elif isinstance(object, bytes):
            self._bytes = object
        else:
            raise TypeError("Cannot convert object of type %r"
                            % (type(object)))

    def _to_text(self):
        raise TypeError("Cannot implicitly decode octets instance")

    if six.PY2:
        __unicode__ = _to_text
        __unicode__.__name__ = "__unicode__"

        def __iter__(self):
            return iter(self._bytes)

        def __mod__(self, to_interpolate):
            format_string = _BYTES_FORMAT.sub(to_interpolate, r'%\1s')
            return format_string % to_interpolate

        def __getitem__(self, key):
            return self._bytes[key]

    elif six.PY3:
        __str__ = _to_text
        __str__.__name__ = "__str__"

        def __iter__(self):
            for i in range(len(self._bytes)):
                yield self._bytes[i:i + 1]

        def __getitem__(self, key):
            if isinstance(key, slice):
                return self._bytes[key]
            elif isinstance(key, six.integer_types):
                self._bytes[key]  # for the IndexError
                upperbound = None if key == -1 else key + 1
                return self._bytes[key:upperbound]
            else:
                raise TypeError("octets indices must be integers")

        if _LESS_THAN_PY35:
            def __mod__(self, to_interpolate):
                def _decode(thing):
                    if isinstance(thing, bytes):
                        return thing.decode('charmap')
                    elif isinstance(thing, six.text_type):
                        raise TypeError("Cannot implicitly encode unicode.")
                    return thing

                format_string = _decode(self._bytes)
                format_string = _BYTES_FORMAT.sub(format_string, r'%\1s')

                if not isinstance(to_interpolate, (tuple, dict)):
                    to_interpolate = (to_interpolate,)

                if isinstance(to_interpolate, tuple):
                    to_interpolate = tuple(_decode(el)
                                           for el in to_interpolate)
                elif isinstance(to_interpolate, dict):
                    to_interpolate = {_decode(key): _decode(value)
                                      for key, value in to_interpolate.items()}

                formatted = format_string % to_interpolate
                return formatted.encode('charmap')
        else:
            def __mod__(self, to_interpolate):
                return self._bytes % to_interpolate

    del _to_text

    @property
    def bytes(self):
        """
        Return the underlying :py:class:`bytes` object.

        :return: The :py:class:`bytes`: that backs this
                 :py:class:`octets` instance.
        :rtype: :py:class:`bytes`.
        """
        return self._bytes

    def __getattr__(self, attribute):
        return getattr(self._bytes, attribute)

    def __eq__(self, other):
        return self._bytes == other

    def __ne__(self, other):
        return self._bytes != other

    def __lt__(self, other):
        return self._bytes < other

    def __gt__(self, other):
        return self._bytes > other

    def __le__(self, other):
        return self._bytes <= other

    def __ge__(self, other):
        return self._bytes >= other

    def __repr__(self):
        name = self.__class__.__name__
        return "%s(%r)" % (name, self._bytes)
