import os
import io


class ChunkIO:
    def __init__(self, base_dir: os.PathLike, bytes_per_chunk: int, mode: str):
        if mode in ['r','rb']:
            if not os.listdir(base_dir):
                raise OSError("Input directory empty")
            self.__mode = 'rb'
            setattr(self, 'write', self.__wrong_mode)
        elif mode in ['w','wb']:
            for file in os.listdir(base_dir):
                if file.startswith('chunk-'):
                    raise OSError("Output directory contains file(s) named 'chunk-*")
            self.__mode = 'wb'
            setattr(self, 'read', self.__wrong_mode)
        else:
            raise ValueError(f"Unknown mode '{mode}'")
            setattr(self, 'write', self.__wrong_mode)
            setattr(self, 'read',  self.__wrong_mode)

        self.__base_dir = base_dir
        self.__bytes_per_chunk = bytes_per_chunk
        
        self.__closed = False
        self.__chunk_index = 0
        self.__byte_index = 0
        self.__opened_chunk = None
        self.__switch_to_next_chunk()
    
    @property
    def base_dir(self) -> os.PathLike:
        return self.__base_dir

    @property
    def bytes_per_chunk(self) -> int:
        return self.__bytes_per_chunk
    
    @property
    def mode(self) -> str:
        return self.__mode
    
    @property
    def closed(self) -> bool:
        return self.__closed
    
    @property
    def chunk_index(self) -> int:
        return self.__chunk_index
    
    @property
    def byte_index(self) -> int:
        return self.__byte_index
    
    def net_bytes_written(self) -> int:
        """ Returns the amount of bytes written, in total. """
        return self.__bytes_per_chunk * self.__chunk_index + self.__byte_index
    
    def __wrong_mode(self) -> None:
        raise OSError("Stream is in improper mode")
    
    def __switch_to_next_chunk(self) -> None:
        # finalize existing chunk
        if self.__opened_chunk is not None:
            #print(f"Finalized chunk {self.__chunk_index}")
            self.__opened_chunk.close()
        # reset chunk data
        self.__chunk_index += 1
        self.__byte_index = 0
        # open new chunk
        next_name = os.path.join(self.__base_dir, f"chunk-{self.__chunk_index}")
        self.__opened_chunk = open(next_name, self.__mode)
    
    def close(self) -> None:
        # check double-closing
        if self.__closed:
            raise OSError("ChunkIO already closed")
        self.__closed = False
        # close last chunk
        if self.__opened_chunk is not None:
            #print(f"Closed chunk {self.__chunk_index}")
            self.__opened_chunk.close()
    
    def read(self, n: int = -1):
        # check closed
        if self.closed:
            raise OSError("ChunkIO closed, cannot read")
        # anything left to read?
        if self.__opened_chunk is None:
            return None
        # read bytes
        allread = bytes()
        while n != 0:
            # read what we need from the current chunk
            read = self.__opened_chunk.read(n)
            allread += read
            n -= len(read)
            # get a new chunk if this one is drained
            if n != 0:
                try:
                    self.__switch_to_next_chunk()
                except FileNotFoundError:
                    self.__opened_chunk = None  # already closed
                    return allread
        return allread

    def write(self, buf) -> int:
        # check closed
        if self.closed:
            raise OSError("ChunkIO closed, cannot write")
        # check type
        if not isinstance(buf, bytes):
            raise TypeError("a bytes-like object is required")
        buf = io.BytesIO(buf)
        # write bytes
        total = 0
        n = self.__bytes_per_chunk - self.__byte_index
        while (b:=buf.read(n)):
            nread = len(b)
            # write what we read to the current chunk
            total += nread
            self.__byte_index += nread
            self.__opened_chunk.write(b)
            # get a new chunk if this one was filled
            n -= nread
            if n == 0:
                self.__switch_to_next_chunk()
                n = self.__bytes_per_chunk
        return total
