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

# How to use: csv2tb.py <csv-file>.glif <tb-file>.tb

# This script will mine a csv file for notes over time and puts the
# results into a tb file compatible with Turtle Blocks JS.

# In this version, the follow assumptions are made:
# Row 1 is header
# Column 1 is date
# Rhythm is 4 8 8 4...

import os
import re
import sys

RHYTHM = [4, 8, 8, 4]
SKIPCOL = [0, 5]
SKIPROW = [0]

def from_csv_to_tb(csvfile, tbfile):
    csvfd = open(csvfile, "r")
    tbfd = open(tbfile, "w")

    block_count = 0

    # Open tb list
    tbfd.write('[')

    # output a new action block and label
    tbfd.write(
        '[%d,["action",{"collapsed":false}],100,200,[null,%d,%d,null]],' % (
            block_count, block_count + 1, block_count + 2))
    tbfd.write('[%d,["text",{"value":"notes"}],0,0,[%d]]' % (
        block_count + 1, block_count))

    block_count += 2;

    line_count = 0

    for line in csvfd:
        if line_count in SKIPROW:
            print ('skipping line %d' % (line_count))
            line_count += 1  # increment no matter what
            continue

        line_count += 1

        cols = line.split(',')
        
        note_value_index = 0
        for i in range(len(cols)):
            if i in SKIPCOL:
                continue

            hertz = cols[i]
            note_value = RHYTHM[note_value_index % len(RHYTHM)]

            note_value_index += 1

            print ('new note %d: %f %d\n' % (i, float(hertz), int(note_value)))
            # Write trailing comma here
            if block_count == 2:
                # add trailing comma to action block stack
                tbfd.write(',')
                prev_block = 0;
            else:
                # finish off last hidden block
                tbfd.write('%d]],' % (block_count))
                prev_block = block_count - 1;

            tbfd.write('[%d,"newnote",0,0,[%d,%d,%d,%d]],'
                       % (block_count, prev_block, block_count + 1,
                          block_count + 4, block_count + 7))
            tbfd.write('[%d,"divide",0,0,[%d,%d,%d]],'
                       % (block_count + 1, block_count, block_count + 2,
                          block_count + 3))
            tbfd.write('[%d,["number",{"value":1}],0,0,[%d]],'
                       % (block_count + 2, block_count + 1))
            tbfd.write('[%d,["number",{"value":%d}],0,0,[%d]],'
                       % (block_count + 3, note_value, block_count + 1))
            tbfd.write('[%d,"vspace",0,0,[%d,%d]],'
                       % (block_count + 4, block_count, block_count + 5))
            tbfd.write('[%d,"hertz",0,0,[%d,%d,null]],'
                       % (block_count + 5, block_count + 4, block_count + 6))
            tbfd.write('[%d,["number",{"value":%f}],0,0,[%d]],'
                       % (block_count + 6, float(hertz), block_count + 5))
            tbfd.write('[%d,"hidden",0,0,[%d,'
                       % (block_count + 7, block_count))

            block_count += 8;

    if block_count > 2:
        tbfd.write('null]]')  # last hidden block goes no where

    tbfd.write(']')

    csvfd.close()
    tbfd.close()

    return


if __name__ == '__main__':
    ini = from_csv_to_tb(sys.argv[1], sys.argv[2])
