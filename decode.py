# disclude-from-build 6:6

import os
import gzip
import json

from chunkio import ChunkIO


def decode(
    indir: os.PathLike,
    outdir: os.PathLike
):
    """
    :3
    """

    indir = os.path.abspath(indir)
    outdir = os.path.abspath(outdir)

    # check arguments
    if not os.path.exists(indir):
        raise FileNotFoundError(indir)
    if not os.path.exists(outdir):
        raise FileNotFoundError(outdir)
    if not os.path.isdir(indir):
        raise OSError(f"Input directory '{indir}' not a directory")
    if not os.path.isdir(outdir):
        raise OSError(f"Output directory '{outdir}' not a directory")

    # read and parse header
    if not os.path.exists(os.path.join(indir, 'header')):
        raise OSError("Input directory does not contain 'header' file")
    with open(os.path.join(indir, 'header'), 'r') as file:
        try:
            header = json.load(file)
        except Exception as e:
            print(repr(e))
            raise OSError("Invalid header file")

    # check chunk count
    for i in range(1, header['chunk-count']+1):
        if not os.path.exists(os.path.join(indir, f'chunk-{i}')):
            raise OSError(f"Input directory does not contain 'chunk-{i}' file " + \
                          f"(header calls for {header['chunk-count']})")

    # set up input stream
    use_compression = (header['compression'] == 'gzip')
    chunkreader = ChunkIO(indir, header['chunk-size'], 'rb')
    if use_compression:
        gzipreader = gzip.GzipFile(fileobj=chunkreader, mode='rb')

    # read in file(s) and their sizes
    markers = list(sorted(header['markers'].items(), key=lambda item: item[1]))
    filesizes = []
    oldend = 0
    for filename,endpos in markers:
        filesizes.append( (filename, endpos-oldend) )
        oldend = endpos
    
    # read from input stream and write to output files
    try:
        for filename,size in filesizes:
            if use_compression:
                filedata = gzipreader.read(size)
            else:
                filedata = chunkreader.read(size)
            fullname = os.path.join(outdir, filename)
            folder = os.path.dirname(fullname)
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(fullname, 'wb') as file:
                file.write(filedata)

    # crude error handling
    except Exception as e:
        print(f"Error: {repr(e)}")
        raise e

    # print marker results
    else:
        max_title_size = max(map(lambda it: len(it[0]), filesizes))
        max_bytes_size = max(map(lambda it: len(str(it[1])), filesizes))
        print()
        print('File'.ljust(max_title_size) + '  ' + 'Size'.rjust(max_bytes_size))
        print('-'*(max_title_size+max_bytes_size+2))
        for file,size in filesizes:
            filestr = str(file).ljust(max_title_size)
            sizestr = str(size).rjust(max_bytes_size)
            print(filestr + '  ' + sizestr)

    # close output stream
    finally:
        if use_compression:
            gzipreader.close()
        chunkreader.close()
