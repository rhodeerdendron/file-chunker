# disclude-from-build 7:7

import os
import gzip
import json

from chunkio import ChunkIO


def encode(
    infile: os.PathLike,
    outdir: os.PathLike,
    use_compression: bool,
    bytes_per_chunk: int
):
    """
    :3
    """

    infile = os.path.abspath(infile)
    outdir = os.path.abspath(outdir)

    # check arguments
    if not os.path.exists(infile):
        raise FileNotFoundError(infile)
    if not os.path.exists(outdir):
        raise FileNotFoundError(outdir)
    if not os.path.isdir(outdir):
        raise OSError(f"Output directory '{outdir}' not a directory")
    for file in os.listdir(outdir):
        if file == 'header':
            raise OSError("Output directory contains file named 'header' (hint: use an empty directory?)")
        elif file.startswith('chunk-'):
            raise OSError("Output directory contains file(s) named 'chunk-*' (hint: use an empty directory?)")

    # walk file(s)
    infiles = []
    prefix = os.path.dirname(infile)
    if os.path.isfile(infile):
        # just a single file was supplied
        infiles = [infile]
    else:
        # a directory was supplied -- walk it
        for root,dirs,files in os.walk(infile):
            infiles.extend([os.path.join(root, file) for file in files])
    if not len(infiles):
        print("No files found to encode, returning.")
        return

    # set up output stream
    chunkwriter = ChunkIO(outdir, bytes_per_chunk, 'wb')
    if use_compression:
        gzipwriter = gzip.GzipFile(fileobj=chunkwriter, mode='wb')

    # read in file(s), and write to output stream
    try:
        markers = {}
        total_bytes = 0
        for path in infiles:
            with open(path, 'rb') as file:
                if use_compression:
                    gzipwriter.write(file.read())
                else:
                    chunkwriter.write(file.read())
                relpath = os.path.relpath(path, prefix)
                total_bytes += file.tell()  # we should be at the end of this file?
                markers[relpath] = total_bytes

    # crude error handling
    except Exception as e:
        print(f"Error: {repr(e)}")
        raise

    # close output stream
    finally:
        if use_compression:
            gzipwriter.close()
        chunkwriter.close()
    
    # print marker results
    max_title_size = max(map(len, markers.keys()))
    max_bytes_size = max(map(lambda v: len(str(v)), markers.values()))
    print()
    print('File'.ljust(max_title_size) + '  ' + 'Pos'.rjust(max_bytes_size))
    print('-'*(max_title_size+max_bytes_size+2))
    for file,size in markers.items():
        filestr = str(file).ljust(max_title_size)
        sizestr = str(size).rjust(max_bytes_size)
        print(filestr + '  ' + sizestr)
    
    # emit header
    with open(os.path.join(outdir, 'header'), 'w') as file:
        json.dump({
            'version': 1.0,
            'chunk-count': chunkwriter.chunk_index,
            'chunk-size': bytes_per_chunk,
            'compression': 'gzip' if use_compression else None,
            'markers': markers
        }, file, indent=None)
