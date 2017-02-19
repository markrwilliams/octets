import pytest
import six
from hypothesis import given, strategies as st
from octets import octets


@given(
    number=st.integers() | st.floats() | st.decimals(),
)
def test_numeric_types(number):
    """
    Numbers are their ``ascii``, base 10 representation.
    """
    assert octets(number) == six.text_type(number).encode('ascii')


@given(
    text=st.text(),
    encoding=st.sampled_from([None, 'ascii', 'utf-8']),
    errors=st.sampled_from([None, 'backslashreplace'])
)
def test_text(text, encoding, errors):
    """
    Text is encoded to bytes using the provided encoding, with a
    :py:exc:`TypeError` being raised when the encoding is
    :py:const:`None`.
    """
    try:
        encoded = octets(text, encoding, errors)
    except TypeError:
        assert encoding is None
    except UnicodeEncodeError:
        assert errors is None
    else:
        args = (encoding,) + ((errors,) if errors else ())
        assert encoded == text.encode(*args)


@given(
    byte_strings=st.binary(),
)
def test_bytes(byte_strings):
    """
    Byte strings are passed through.
    """
    assert octets(byte_strings) == byte_strings


@pytest.mark.parametrize("obj", [object(), [b"bytes"], {b"byte": 1}])
def test_unknown_type(obj):
    """
    Instances that aren't numbers, text, or bytes raise a
    :py:exc:`TypeError`.
    """
    with pytest.raises(TypeError):
        octets(obj)


def test_to_text_type():
    """
    Attempting to convert an :py:class:`octets` instance to a text
    type raises a :py:exc:`TypeError`.
    """
    with pytest.raises(TypeError):
        six.text_type(octets(b'bytes'))


@given(
    byte_string=st.binary(),
)
def test_iter(byte_string):
    """
    Iteration yields single character byte strings.
    """
    assert list(octets(byte_string)) == [
        b.encode('charmap')
        for b in byte_string.decode('charmap')
    ]


@given(
    byte_string=st.binary(),
    index=st.integers(),
)
def test_getitem(byte_string, index):
    """
    Accessing a single index returns a single character string.
    """
    try:
        char = octets(byte_string)[index]
    except IndexError:
        assert not byte_string or abs(index) > (len(byte_string) - 1)
    else:
        assert char == byte_string.decode('charmap')[index].encode('charmap')


@given(
    byte_string=st.binary(),
    lower=st.integers() | st.just(None),
    upper=st.integers() | st.just(None),
    step=st.integers().filter(lambda i: i != 0) | st.just(None),
)
def test_getitem_slice(byte_string, lower, upper, step):
    """
    Accessing a slice returns the correspoding sequence of characters.
    """
    sequence = byte_string.decode('charmap')[lower:upper:step]
    assert octets(byte_string)[lower:upper:step] == sequence.encode('charmap')


def test_getitem_unsupported_index():
    """
    Indices must be integers or slices.
    """
    with pytest.raises(TypeError):
        octets(b'bytes')[object()]
