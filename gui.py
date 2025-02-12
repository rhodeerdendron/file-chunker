# disclude-from-build 13:14

import os
import io

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as tkfd
from tkinter import scrolledtext as tkst

from typing import List

from encode import encode
from decode import decode


def build_encode_tab(tab_encode: ttk.Frame) -> dict:
    """
    Builds the 'encode' tab and adds it to the given frame.

    Returns:
    {
        'in_file': tk.StringVar,
        'out_dir': tk.StringVar,
        'compression': tk.BooleanVar,
        'chunk_size': tk.IntVar,
        'log_file': tk.scrolledtext.ScrolledText
    }
    """

    frame_settings = {
        'fill': 'both',
        'padx': 6,
        'pady': (4,6),
        'ipady': 4
    }

    # =============
    # In-file frame

    infile_frame = ttk.Labelframe(tab_encode, text='Input')
    infile_frame.pack(**frame_settings)

    infile_var = tk.StringVar(value="")
    def choose_infile_file():
        # get picked file or directory
        path = tkfd.askopenfilename()
        if not path: return
        path = os.path.abspath(path)
        infile_var.set(path)
        print("Infile", path)
        # quick validity check
        valid = os.path.exists(path)
        infile_chosen.config(foreground='' if valid else 'red')
    def choose_infile_dir():
        # get picked file or directory
        path = tkfd.askdirectory()
        if not path: return
        path = os.path.abspath(path)
        infile_var.set(path)
        print("Infile", path)
        # quick validity check
        valid = os.path.exists(path)
        infile_chosen.config(foreground='' if valid else 'red')

    infile_button_label_frame = ttk.Frame(infile_frame)
    infile_button_file = ttk.Button(
        infile_button_label_frame,
        text='File...',
        command=choose_infile_file
    )
    infile_button_dir = ttk.Button(
        infile_button_label_frame,
        text='Directory...',
        command=choose_infile_dir
    )
    infile_label = ttk.Label(
        infile_button_label_frame,
        text='File or directory to encode:'
    )
    infile_label.pack(side="left", fill='x', expand=1)
    infile_button_dir.pack(side="right", fill='x')
    infile_button_file.pack(side="right", fill='x')

    infile_chosen = ttk.Label(
        infile_frame,
        textvariable=infile_var
    )
    infile_button_label_frame.pack(padx=5, side="top", fill='x', expand=1)
    infile_chosen.pack(padx=5, pady=(0,6), side="bottom", fill='x', expand=1)

    # =============
    # Out-dir frame

    outdir_frame = ttk.Labelframe(tab_encode, text='Output')
    outdir_frame.pack(**frame_settings)

    outdir_var = tk.StringVar(value="")
    def choose_outdir():
        # get picked directory
        path = tkfd.askdirectory()
        if not path: return
        path = os.path.abspath(path)
        outdir_var.set(path)
        print("Outdir", path)
        # quick validity check
        valid = os.path.isdir(path)
        outdir_chosen.config(foreground='' if valid else 'red')

    outdir_button_label_frame = ttk.Frame(outdir_frame)
    outdir_button = ttk.Button(
        outdir_button_label_frame,
        text='Choose...',
        command=choose_outdir
    )
    outdir_label = ttk.Label(
        outdir_button_label_frame,
        text='Chunk output directory:'
    )
    outdir_label.pack(side="left", fill='x', expand=1)
    outdir_button.pack(side="right", fill='x')

    outdir_chosen = ttk.Label(
        outdir_frame,
        textvariable=outdir_var
    )
    outdir_button_label_frame.pack(padx=5, side="top", fill='x', expand=1)
    outdir_chosen.pack(padx=5, pady=(0,6), side="bottom", fill='x', expand=1)

    # =============
    # Settings frame

    settings_frame = ttk.Labelframe(tab_encode, text='Settings')
    settings_frame.pack(**frame_settings)

    settings_frame_settings = {
        'padx': 5,
        'pady': 4,
        'side': 'top',
        'fill': 'x',
        'expand': 1
    }

    compression_var = tk.BooleanVar(value=False)
    compression_checkbox = ttk.Checkbutton(
        settings_frame,
        text='Compress input?',
        variable=compression_var
    )
    compression_checkbox.pack(**settings_frame_settings)

    chunk_size_var = tk.IntVar(value=10)
    chunk_size_frame = ttk.Frame(settings_frame)
    chunk_size_label = ttk.Label(
        chunk_size_frame,
        text='Chunk size?'
    )
    chunk_size_10 = ttk.Radiobutton(
        chunk_size_frame,
        text='10 MB',
        value=10,
        variable=chunk_size_var
    )
    chunk_size_50 = ttk.Radiobutton(
        chunk_size_frame,
        text='50 MB',
        value=50,
        variable=chunk_size_var
    )
    chunk_size_500 = ttk.Radiobutton(
        chunk_size_frame,
        text='500 MB',
        value=500,
        variable=chunk_size_var
    )
    chunk_size_label.grid(row=0, column=0, padx=5)
    chunk_size_10.grid(row=0, column=1)
    chunk_size_50.grid(row=0, column=2)
    chunk_size_500.grid(row=0, column=3)
    chunk_size_frame.pack(**settings_frame_settings)

    # =============
    # Encode button

    encode_button = ttk.Button(
        tab_encode,
        text='Encode'
    )
    encode_button.pack(pady=4)

    # =============
    # Log frame

    log_frame = ttk.Labelframe(tab_encode, text='Log')
    log_frame.pack(**frame_settings, expand=1, side='bottom')

    log_output_text = tkst.ScrolledText(
        log_frame,
        state='disabled',
        wrap='char')
    log_output_text.pack(fill='both', expand=1, side='top')

    # =============
    # Finalize encode tab

    def do_encode():
        infile = infile_var.get()
        outdir = outdir_var.get()
        if not infile.strip() or not outdir.strip():
            return
        compression = compression_var.get()
        chunksize = chunk_size_var.get() * 1024 * 1024
        encode(infile, outdir, compression, chunksize)
    
    encode_button['command'] = do_encode

    return {
        'in_file': infile_var,
        'out_dir': outdir_var,
        'compression': compression_var,
        'chunk_size': chunk_size_var,
        'log_file': log_output_text
    }


def build_decode_tab(tab_decode: ttk.Frame) -> dict:
    """
    Builds the 'decode' tab and adds it to the given frame.

    Returns:
    {
        'in_dir': tk.StringVar,
        'out_dir': tk.StringVar,
        'log_file': tk.scrolledtext.ScrolledText
    }
    """

    frame_settings = {
        'fill': 'both',
        'padx': 6,
        'pady': (4,6),
        'ipady': 4
    }

    # =============
    # In-dir frame

    indir_frame = ttk.Labelframe(tab_decode, text='Input')
    indir_frame.pack(**frame_settings)

    indir_var = tk.StringVar(value="")
    def choose_indir():
        # get picked directory
        path = tkfd.askdirectory()
        if not path: return
        path = os.path.abspath(path)
        indir_var.set(path)
        print("indir", path)
        # quick validity check
        valid = os.path.isdir(path)
        indir_chosen.config(foreground='' if valid else 'red')

    indir_button_label_frame = ttk.Frame(indir_frame)
    indir_button = ttk.Button(
        indir_button_label_frame,
        text='Choose...',
        command=choose_indir
    )
    indir_label = ttk.Label(
        indir_button_label_frame,
        text='Chunks directory to decode:'
    )
    indir_label.pack(side="left", fill='x', expand=1)
    indir_button.pack(side="right", fill='x')

    indir_chosen = ttk.Label(
        indir_frame,
        textvariable=indir_var
    )
    indir_button_label_frame.pack(padx=5, side="top", fill='x', expand=1)
    indir_chosen.pack(padx=5, pady=(0,6), side="bottom", fill='x', expand=1)

    # =============
    # Out-dir frame

    outdir_frame = ttk.Labelframe(tab_decode, text='Output')
    outdir_frame.pack(**frame_settings)

    outdir_var = tk.StringVar(value="")
    def choose_outdir():
        # get picked directory
        path = tkfd.askdirectory()
        if not path: return
        path = os.path.abspath(path)
        outdir_var.set(path)
        print("Outdir", path)
        # quick validity check
        valid = os.path.isdir(path)
        outdir_chosen.config(foreground='' if valid else 'red')

    outdir_button_label_frame = ttk.Frame(outdir_frame)
    outdir_button = ttk.Button(
        outdir_button_label_frame,
        text='Choose...',
        command=choose_outdir
    )
    outdir_label = ttk.Label(
        outdir_button_label_frame,
        text='Decoded file output directory:'
    )
    outdir_label.pack(side="left", fill='x', expand=1)
    outdir_button.pack(side="right", fill='x')

    outdir_chosen = ttk.Label(
        outdir_frame,
        textvariable=outdir_var
    )
    outdir_button_label_frame.pack(padx=5, side="top", fill='x', expand=1)
    outdir_chosen.pack(padx=5, pady=(0,6), side="bottom", fill='x', expand=1)

    # =============
    # Decode button

    decode_button = ttk.Button(
        tab_decode,
        text='Decode'
    )
    decode_button.pack(pady=4)

    # =============
    # Log frame

    log_frame = ttk.Labelframe(tab_decode, text='Log')
    log_frame.pack(**frame_settings, expand=1, side='bottom')

    log_output_text = tkst.ScrolledText(
        log_frame,
        state='disabled',
        wrap='char')
    log_output_text.pack(fill='both', expand=1, side='top')

    # =============
    # Finalize decode tab

    def do_decode():
        indir = indir_var.get()
        outdir = outdir_var.get()
        if not indir.strip() or not outdir.strip():
            return
        decode(indir, outdir)
    
    decode_button['command'] = do_decode

    return {
        'in_dir': indir_var,
        'out_dir': outdir_var,
        'log_file': log_output_text
    }


_oldprint = print
_guiprint_outputs: List[tkst.ScrolledText] = []
def set_new_print_function():
    # this is a disgusting hack, but it works
    def _guiprint(*args, **kwargs):
        # print to buffer
        global _oldprint
        buf = io.StringIO()
        kwargs['file'] = buf
        _oldprint(*args, **kwargs)
        output_str = buf.getvalue()
        buf.close()
        _oldprint(output_str, end='')
        # write to log panes
        global _guiprint_outputs
        for output in _guiprint_outputs:
            output['state'] = 'normal'
            output.insert('end', output_str)
            output['state'] = 'disabled'
    print = _guiprint


def run_gui():
    root = tk.Tk()
    root.title("Discord compressor")
    root.geometry('600x600')

    style = ttk.Style()
    style.theme_use('alt')

    tabroot = ttk.Notebook(root)

    tab_encode = ttk.Frame(tabroot)
    tab_decode = ttk.Frame(tabroot)
    
    tabroot.add(tab_encode, text='Encode')
    tabroot.add(tab_decode, text='Decode')
    tabroot.pack(expand=1, fill='both')

    encode_vars = build_encode_tab(tab_encode)
    decode_vars = build_decode_tab(tab_decode)

    global _guiprint_outputs
    _guiprint_outputs.append(encode_vars['log_file'])
    _guiprint_outputs.append(decode_vars['log_file'])
    set_new_print_function()

    root.mainloop()

if __name__ == '__main__':
    run_gui()
