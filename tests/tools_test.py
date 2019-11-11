import binaryread.tools as tools
import io

def test_readu8():
    input = io.BytesIO(bytes([128]))
    assert 128 == tools.readu8(input)


def test_read8():
    input = io.BytesIO(bytes([128]))
    assert -128 == tools.read8(input)


def test_readu16():
    input = io.BytesIO(bytes([255, 128]))
    assert 33023 == tools.readu16(input)


def test_read16():
    input = io.BytesIO(bytes([255, 128]))
    assert -32513 == tools.read16(input)


def test_readu32():
    input = io.BytesIO(bytes([64, 32, 255, 128]))
    assert 2164203584 == tools.readu32(input)


def test_read32():
    input = io.BytesIO(bytes([64, 32, 255, 128]))
    assert -2130763712 == tools.read32(input)


def test_readfloat():
    input = io.BytesIO(bytes([0x00, 0x00, 0xc0, 0xbf]))
    assert -1.5 == tools.readfloat(input)


def test_read_partial_stream():
    input = io.BytesIO(bytes([0x00] * 4097))
    partial_stream = tools.read_partial_stream(input, 0, 4097)
    
    first_block = next(partial_stream)
    assert 4096 == len(first_block)
    
    last_block = next(partial_stream)
    assert 1 == len(last_block)
    


def test_stream_bits_one_byte():
    b = [0]
    assert [0] == list(tools.stream_bits(b,  8))
    assert [0, 0] == list(tools.stream_bits(b,  4))


    b = [15]
    assert [15] == list(tools.stream_bits(b,  8))
    assert [0, 15] == list(tools.stream_bits(b,  4))
    assert [0, 0, 0, 0, 1, 1, 1, 1] == list(tools.stream_bits(b,  1))
    
    b = [240]
    assert [240] == list(tools.stream_bits(b,  8))
    assert [15, 0] == list(tools.stream_bits(b,  4))
    assert [1, 1, 1, 1, 0, 0, 0, 0] == list(tools.stream_bits(b,  1))

    b = [255]
    assert [255] == list(tools.stream_bits(b,  8))
    assert [15, 15] == list(tools.stream_bits(b,  4))
    assert [1, 1, 1, 1, 1, 1, 1, 1] == list(tools.stream_bits(b,  1))

    b = [255] # 111 111 11
    assert [7, 7, 3] == list(tools.stream_bits(b,  3))
    
    b = [227] # 111 0000 11
    assert [7, 0, 3] == list(tools.stream_bits(b,  3))

def test_stream_bits_multiple_bytes():
    b = [0, 0]
    assert [0, 0] == list(tools.stream_bits(b,  8))
    assert [0, 0, 0, 0] == list(tools.stream_bits(b,  4))

    b = [255, 0]
    assert [255, 0] == list(tools.stream_bits(b,  8))
    assert [15, 15, 0, 0] == list(tools.stream_bits(b,  4))

    b = [0, 255]
    assert [0, 255] == list(tools.stream_bits(b,  8))
    assert [0, 0, 15, 15] == list(tools.stream_bits(b,  4))

    b = [227, 142]  #11100 011|10 00111 0
    assert [7, 0, 7, 0, 7, 0] == list(tools.stream_bits(b,  3))
    assert [28, 14, 7,  0] == list(tools.stream_bits(b,  5))


