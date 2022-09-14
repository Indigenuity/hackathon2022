import codecs
import io
# from os import SEEK_SET
from itertools import zip_longest
from typing import Optional, List, Iterable

import boto3

from s3zero.safe_utf8 import SafeUTF8Iterator

from base64io import Base64IO


S3_MAX_KEY_LENGTH = 1024        # Objects in s3 have a max length of 1024 bytes for utf-8 encoded strings
ORDINAL_DELIMITER = ":"         # The character between the ordinal character(s) and the chunk values
S3_ENCODING = "utf8"            # S3 requires UTF-8 encoded strings for keys


class S3ZeroRaw(io.BufferedIOBase):

    closed = False
    __readable = False
    __writable = False

    def __init__(self, bucket: str, key_prefix: str = "", mode: str = "r", client=None, chunk_header_length=1, chunk_header_generator=None, encoding="base64"):
        """
        Note that chunk_header_length=1 can support blobs of up to 141048832 when using SafeUTF8Iterator.  Also depends
        on the length of the key prefix
        """
        super().__init__()
        self.__bucket = bucket
        self.__key_prefix = key_prefix
        self.__client = client if client else boto3.client('s3')

        self.__read_buffer = b""
        self.__write_buffer = b""

        self.mode = mode
        if self.mode == "r":
            self.__readable = True
        elif self.mode == "w":
            self.__writable = True
        else:
            raise ValueError("mode must be 'r' or 'w'")

        self.__chunk_length = S3_MAX_KEY_LENGTH - len(self.__key_prefix.encode("utf-8"))
        self.__chunk_header_length = chunk_header_length
        # TODO figure out a replacement iterator, where the header will have constant byte length. for now, just pad length by 4
        self.__chunk_header_generator = chunk_header_generator if chunk_header_generator else SafeUTF8Iterator(digits=self.__chunk_header_length)
        self.__chunk_body_length = S3_MAX_KEY_LENGTH - len(self.__key_prefix.encode("utf-8")) - self.__chunk_header_length - 4

        self.__encoding = encoding

    def __enter__(self):
        """Return self on enter."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Properly close self on exit."""
        self.close()
        return False

    def _check_closed(self):
        if self.closed:
            raise ValueError("IO stream is closed")

    def __chunker(self, iterator):
        """
        Take some bytes or a string (or really any iterator), and return the first n bytes, based on this streams chunk size
        This is built using the itertools recipes
        """
        args = [iter(iterator)] * self.__chunk_body_length
        return zip_longest(*args)

    def read_all(self):
        paginator = self.__client.get_paginator('list_objects_v2')
        operation_parameters = {'Bucket': self.__bucket,
                                'Prefix': self.__key_prefix}
        page_iterator = paginator.paginate(**operation_parameters)
        for page in page_iterator:
            for key in page['Contents']:
                content = key['Key'].split(self.__key_prefix)[1].split(ORDINAL_DELIMITER)[1]
                self.__read_buffer += content.encode(S3_ENCODING)\

        return codecs.decode(self.__read_buffer, self.__encoding)

    # ------------------------------------------------------------------------------------------------------------------
    # IOBase overrides
    # ------------------------------------------------------------------------------------------------------------------

    def close(self):
        """Close this stream, encoding and writing any buffered bytes is present."""
        self.flush()
        self.closed = True

    def fileno(self) -> int:
        raise OSError("This IO Object does not use OS file descriptors")

    def flush(self):
        if self.__write_buffer:
            self.__write_next_object(self.__write_buffer)
            self.__write_buffer = b""

    def isatty(self) -> bool:
        return False

    def readable(self):
        self._check_closed()
        return self.__readable

    def readline(self, __size: Optional[int] = ...) -> bytes:
        raise NotImplemented()

    def readlines(self, __hint: int = ...) -> List[bytes]:
        raise NotImplemented()

    def seek(self, __offset: int, __whence: int = ...) -> int:
        raise NotImplemented()

    def seekable(self) -> bool:
        return False

    def tell(self) -> int:
        raise NotImplemented()

    def truncate(self, __size: Optional[int] = ...) -> int:
        raise NotImplemented()

    def writable(self):
        self._check_closed()
        return self.__writable

    def writelines(self, __lines: Iterable) -> None:
        """
        Accepts bytes, converts to utf-8 encoded strings and sends them to __write_line
        """
        for line in __lines:
            self.write(line)


    # ------------------------------------------------------------------------------------------------------------------
    # BufferedIOBase overrides
    # ------------------------------------------------------------------------------------------------------------------

    def detach(self):
        raise io.UnsupportedOperation()

    def read(self, __size: Optional[int] = ...) -> bytes:
        raise NotImplemented()

    def read1(self, __size: int = ...) -> bytes:
        raise NotImplemented()

    def readinto(self, __buffer) -> int:
        raise NotImplemented()

    def readinto1(self, __buffer) -> int:
        raise NotImplemented()

    def write(self, b) -> int:
        self._check_closed()
        if not self.writable():
            raise IOError("Stream is not writable")

        # print(f"got bytes: {b}")
        # TODO figure out how to improve performance here (or if necessary?)
        # Encode the bytes using an encoding that guarantees it can be decoded into "safe" UTF8 characters
        # gotta replace \n because some dumb shit decided encoding in b64 should add newlines: https://stackoverflow.com/questions/30647219/remove-the-new-line-n-from-base64-encoded-strings-in-python3
        _encoded_bytes = codecs.encode(b, self.__encoding).replace(b"\n", b"")
        # print(f"encoded_bytes: {_encoded_bytes}")

        # Load any stashed bytes and clear the buffer
        _bytes_to_write = self.__write_buffer + _encoded_bytes
        self.__write_buffer = b""
        total_length = len(_bytes_to_write)
        print(f"Total bytes to write: {total_length}")

        # print(f"safe String: {_safe_string}")



        # write one chunk at a time,
        # for chunk in self.__chunker(_string_to_write):
        for i in range(0, len(_bytes_to_write), self.__chunk_body_length):
            chunk = _bytes_to_write[i:i+self.__chunk_body_length]
            print(f"writing bytes {i}:{i + self.__chunk_body_length}")
            if len(chunk) == self.__chunk_body_length:
            # if True:
                # print(f"writing chunk: '{chunk}'")
                self.__write_next_object(chunk)
            else:
                # print(f"saving chunk to buffer: '{chunk}'")
                self.__write_buffer = chunk
                # print(f"buffer length: {len(self.__write_buffer)}")

        # There's an unpredictable relationship between bytes received and bytes written. We just guarantee all writes
        # that don't raise an exception.
        return len(b)

    # ------------------------------------------------------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------------------------------------------------------

    def __write_next_object(self, b):
        # if len(b) > self.__chunk_length:
        #     raise ValueError(f"Attempting to write bytes of length {len(b)}, but max chunk length is {self.__chunk_length}")
        content = b.decode(S3_ENCODING)
        key = f"{self.__key_prefix}{self.__chunk_header_generator.next()}{ORDINAL_DELIMITER}{content}"
        # print(f"key: '{key}'")
        self.__client.put_object(Bucket=self.__bucket, Key=key)







    # def close(self):
    #     # type: () -> None
    #     """Close this stream, encoding and writing any buffered bytes is present.
    #     .. note::
    #         This does **not** close the wrapped stream.
    #     """
    #     # if self.__write_buffer:
    #     #     self.__wrapped.write(base64.b64encode(self.__write_buffer))
    #     #     self.__write_buffer = b""
    #     self.__closed = True

