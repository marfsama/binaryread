import struct
import json

from collections import OrderedDict


def readu8(file):
    """ Reads an unsigned byte from the file."""
    data = file.read(1)
    return struct.unpack("B", data)[0]


def read8(file):
    """ Reads a signed byte from the file."""
    data = file.read(1)
    return struct.unpack("b", data)[0]


def readu16(file):
    """ Reads two bytes bytes from the file, treating them as a 16 bit unsigned integer."""
    data = file.read(2)
    return struct.unpack("H", data)[0]


def read16(file):
    """ Reads two bytes bytes from the file, treating them as a 16 bit signed integer."""
    data = file.read(2)
    return struct.unpack("h", data)[0]


def readu32(file):
    """ Reads 4 bytes bytes from the file, treating them as a 32 bit unsigned integer."""
    data = file.read(4)
    return struct.unpack("I", data)[0]


def read32(file):
    """ Reads 4 bytes bytes from the file, treating them as a 32 bit signed integer."""
    data = file.read(4)
    return struct.unpack("i", data)[0]


def readfloat(file):
    """ Reads 4 bytes bytes from the file, treating them as a float."""
    data = file.read(4)
    return struct.unpack("f", data)[0]

# size of byte chunks to read
CHUNK_SIZE = 4096


def read_partial_stream(file, offset, size):
    """Returns an iterator over 4k blocks of byte data.

    Args:
        file: an IOBase Stream, i.e. File
        offset: offset from where to read
        size: size of block to read

    Returns:
        iterator with 4k blocks of byte arrays until the file stream is exhausted or size is reached.

    """
    remaining = size
    file.seek(offset)
    while remaining > 0:
        data = file.read(min(remaining, CHUNK_SIZE))
        if not data:
            raise IOError("unexpected end of stream, {} bytes remaining".format(remaining))
        remaining = remaining - len(data)
        yield data


def read_byte_by_byte(file):
    """Returns the file as a byte by byte iterator."""
    while True:
        yield file.read(1)


def read_terminated_token(file, terminator_function):
    """Returns tokens until a separator is found. the separator is not returned."""
    result = b""
    for byte in read_byte_by_byte(file):
        if terminator_function(byte):
            yield result
            result = b""
        else:
            result = result + byte


def null_terminated(byte):
    """Filter to return true when the byte is 0x00."""
    return byte == b"\x00"


def stream_bits(byte_stream, num_bits=1):
    """Iterates over the byte stream, returning num_bits in each iteration."""
    bits_still_needed = num_bits
    current_value = 0
    for b in byte_stream:
        available_bits = 8
        while available_bits > 0:
            # calculate number of usable bits in current byte
            copy_bits = min(bits_still_needed, available_bits)
            shift_bits = available_bits - copy_bits
            # shift used bits to start of number
            copy_value = b >> shift_bits
            # add current bits to result
            current_value = (current_value << copy_bits) + copy_value
            # calculate bitmask to delete used bits in current byte
            bit_mask = (1 << shift_bits) - 1
            # reduce needed bits by used bits, mask used bits in current byte
            bits_still_needed = bits_still_needed - copy_bits
            b = b & bit_mask
            available_bits = available_bits - copy_bits
            # all required bits gatherd?
            if bits_still_needed == 0:
                # yield the bits
                yield current_value
                # reset current result and reset the number of needed bits
                current_value = 0
                bits_still_needed = num_bits

    # do we have some partial bits processed? yield those
    if bits_still_needed < num_bits:
        yield current_value


# serialisation stuff
def object_attributes_to_ordered_dict(obj,  attributes):
    """Returns the specified attributes  from the object in an OrderedDict."""
    dict = OrderedDict()
    object_vars = vars(obj)
    for attribute in attributes:
        dict[attribute] = object_vars[attribute]
    return dict


class Encoder(json.JSONEncoder):

    """Encoder for json.dumps to automatically serialize objects. The objects should have a function __serialize__(), which return the attibutes to serialize in a dict.
    """

    def default(self, object):
        # is it an object and has the serializeable function? Then use that
        serializable_func = getattr(object, "__serialize__", None)
        if callable(serializable_func):
            return serializable_func()
        # is it a byte array? write as hex string
        if isinstance(object, bytes):
            return ",".join([hex(b) for b in object])
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, object)
