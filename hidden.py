#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2016 - Walter Bender <walter@sugarlabs.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# How to use: hidden.py <input-tb-file>.tb <output-tb-file>.tb

# This script will remove extra hidden blocks from a tb file.

import sys
import json
from json import load as jload
from json import dump as jdump
from StringIO import StringIO

def json_dump(data):
    ''' Save data using available JSON tools. '''
    io = StringIO()
    jdump(data, io)
    return io.getvalue()

def json_load(text):
    ''' Load JSON data using what ever resources are available. '''
    clean_text = text.lstrip()
    # Strip out trailing whitespace, nulls, and newlines
    clean_text = clean_text.replace('\12', '')
    clean_text = clean_text.replace('\00', '')
    clean_text = clean_text.rstrip()
    # Look for missing ']'s
    left_count = clean_text.count('[')
    right_count = clean_text.count(']')
    while left_count > right_count:
        clean_text += ']'
        right_count = clean_text.count(']')
    io = StringIO(clean_text)
    try:
        return jload(io)
    except ValueError:
        # Assume that text is ascii list
        listdata = text.split()
        for i, value in enumerate(listdata):
            listdata[i] = convert(value, float)
        # json converts tuples to lists, so we need to convert back,
        return listdata  # _tuplify(listdata)

def _tuplify(tup):
    ''' Convert to tuples '''
    if not isinstance(tup, list):
        return tup
    return tuple(map(_tuplify, tup))

def data_from_file(ta_file):
    ''' Open the .ta file '''
    file_handle = open(ta_file, 'r')
    text = file_handle.read()
    data = data_from_string(text)
    file_handle.close()
    return data

def data_from_string(text):
    ''' JSON load data from a string. '''
    if isinstance(text, str):
        return json_load(text.replace(']],\n', ']], '))
    elif isinstance(text, unicode):
        text = text.encode('utf-8')
        return json_load(text.replace(']],\n', ']], '))
    else:
        print 'type error (%s) in data_from_string' % (type(text))
        return None

def data_to_file(data, ta_file):
    ''' Write data to a file. '''
    file_handle = file(ta_file, 'w')
    file_handle.write(data_to_string(data))
    file_handle.close()

def data_to_string(data):
    ''' JSON dump a string. '''
    return json_dump(data).replace(', ', ',')

def get_block_name(block):
    if type(block[1] == list):
        return block[1][0]
    else:
        return block[1]

def remove_extra_hidden_blocks(old_file, new_file):
    old_block_data = data_from_file(old_file)

    # We remove one pair per pass, so we have to make multiple passes
    # if there is a hidden block connected to a hidden block connected
    # to a hidden block.
    extra_hidden_blocks = True
    while extra_hidden_blocks:
        extra_hidden_blocks = False
        for i in range(len(old_block_data)):
            if get_block_name(old_block_data[i]) == 'hidden':
                c = old_block_data[i][4][1]
                if c is not None and \
                   get_block_name(old_block_data[c]) == 'hidden':
                    extra_hidden_blocks = True

                    # Remap the connections to bypass extra hidden block.
                    cc = old_block_data[c][4][1]
                    if cc is not None:
                        for j in range(len(old_block_data[cc][4])):
                            if old_block_data[cc][4][j] == c:
                                old_block_data[cc][4][j] = i
                                break
                    old_block_data[i][4][1] = old_block_data[c][4][1]
                    old_block_data[c][4][0] = None
                    old_block_data[c][4][1] = None

    # Now that we have unlinked the hidden blocks, we want to remove
    # them. We can skip them, but we need to change the block numbers
    # as we proceed.

    # Save the original connections 
    original_connections = []
    for i in range(len(old_block_data)):
        connections = []
        for c in range(len(old_block_data[i][4])):
            connections.append(old_block_data[i][4][c])

        original_connections.append(connections)

    for i in range(len(old_block_data)):
        if get_block_name(old_block_data[i]) == 'hidden' and \
           old_block_data[i][4][0] is None and old_block_data[i][4][1] is None:

            # Mark hidden block for deletion.
            old_block_data[i][0] = -1

            # Update all the block numbers > i
            for j in range(len(old_block_data)):
                # Update block number
                if j > i:
                    old_block_data[j][0] -= 1

                # Update connections
                for c in range(len(original_connections[j])):
                    if original_connections[j][c] is not None and \
                       original_connections[j][c] > i:
                        old_block_data[j][4][c] -= 1

    # Skip blocks marked for deletion
    new_block_data = []
    for i in range(len(old_block_data)):
        if old_block_data[i][0] > -1:
            new_block_data.append(old_block_data[i])

    data_to_file(new_block_data, new_file)
    return

if __name__ == '__main__':
    ini = remove_extra_hidden_blocks(sys.argv[1], sys.argv[2])
