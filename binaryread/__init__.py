import os

import binaryread.tools as tools

class Context:
    def __init__(self, file):
        self.file = file
        self.objects = []


class Tell:
    def read(self, context):
        return context.file.tell()


class String:
    def __init__(self, length):
        self.length = length

    def read(self, context):
        string = context.file.read(self.length).decode("utf-8")
        first_nul = string.find("\0")
        if first_nul >= 0:
            return string[:first_nul]
        return string


class Bits:

    """
     Extract :num_bits each from :num_bytes bytes. The length of the result array ist num_bytes // num_bits.
    """

    def __init__(self,  num_bytes, num_bits):
        self.num_bytes = num_bytes
        self.num_bits = num_bits

    def read(self, context):
        bytes = context.file.read(self.num_bytes)
        return list(tools.stream_bits(bytes, self.num_bits))


class Skip:
    def __init__(self, bytes):
        self.bytes = bytes

    def read(self, context):
        return context.file.seek(bytes, os.SEEK_CUR)


class Byte:
    def read(self, context):
        return tools.readu8(context.file)


class Bytes:
    def __init__(self, length):
        self.length = length

    def read(self, context):
        return context.file.read(self.length)


class Short:

    def read(self, context):
        return tools.read16(context.file)


class Word:
    def read(self, context):
        return tools.readu16(context.file)


class Int:

    def read(self, context):
        return tools.read32(context.file)


class Lookup:
    def __init__(self, array, reader, default=None):
        self.array = array
        self.reader = reader
        self.default = default

    def read(self, context):
        index = self.reader.read(context)
        return self.lookup_index(self.default, index)

    def lookup_index(self, default, index):
        if default is None:
            default = index
        try:
            return self.array[index]
        except IndexError:
            return default
        except KeyError:
            return default


class LookupList(Lookup):
    def read(self, context):
        index_list = self.reader.read(context)
        return [self.lookup_index(self.default, index) for index in index_list]


class Loop:
    def __init__(self, count_function, reader):
        self.count_function = count_function
        self.reader = reader

    def read(self, context):
        result = []

        for i in range(self.count_function(context)):
            context.loop_index = i
            result.append(self.reader.read(context))

        context.loop_index = -1
        return result


class Bean:
    def __init__(self, factory, **kwargs):
        self.factory = factory
        self.reader = kwargs

    def read(self, context):
        bean = self.factory()
        context.objects.append(bean)
        for name, reader in self.reader.items():
            result = reader.read(context)
            setattr(bean, name, result)

        context.objects.pop()
        # if the bean has an after_read() method, call it after reading all properties
        if hasattr(bean, 'after_read'):
            bean.after_read(context)

        return bean

