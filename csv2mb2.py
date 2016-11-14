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
# Rows 1-2 are ignored
# Data is in Column 1
# ONE SAMPLES PER ROW: e.g., 0.576883

import os
import re
import sys

RHYTHM = [8]
SKIPCOL = []
SKIPROW = [0, 1, 2]

def from_csv_to_tb(csvfile, tbfile):
    csvfd = open(csvfile, "r")

    line_count = 0
    line_data = [];

    for line in csvfd:
        if not line_count in SKIPROW:
            line_data.append(line);

        line_count += 1

    csvfd.close()

    if len(line_data) < 1:
        return

    cols = line_data[0].split(',')

    tbfd = open(tbfile, "w")

    block_count = 0

    # Open tb list
    tbfd.write('[')

    # Output the action that generates music from the data.
    tbfd.write(
        '[%d,["action",{"collapsed":false}],300,200,[null,%d,%d,null]],' % (
            block_count, block_count + 1, block_count + 2))
    tbfd.write('[%d,["text",{"value":"action"}],0,0,[%d]],' % (
        block_count + 1, block_count))

    block_count += 2;

    col_count = 0;
    for i in range(len(cols)):

        if i in SKIPCOL:
            continue

        if col_count == 0:
            tbfd.write('[%d,["newnote",{}],0,0,[%d,%d,%d,%d]],' % (
                block_count, block_count - 2, block_count + 1,
                block_count + 4, block_count + 7))
        else:
            # Finish off previous note.
            tbfd.write('%d]],' % (block_count))
            # Start new note.
            tbfd.write('[%d,["newnote",{}],0,0,[%d,%d,%d,%d]],' % (
                block_count, block_count - 1, block_count + 1,
                block_count + 4, block_count + 7))

        tbfd.write('[%d,["divide",{}],0,0,[%d,%d,%d]],' % (
            block_count + 1, block_count, block_count + 2,
            block_count + 3))
        tbfd.write('[%d,["number",{"value":1}],0,0,[%d]],' % (
            block_count + 2, block_count + 1))
        tbfd.write('[%d,["number",{"value":%d}],0,0,[%d]],' % (
            block_count + 3, RHYTHM[col_count % len(RHYTHM)], block_count + 1))
        tbfd.write('[%d,["vspace",{}],0,0,[%d,%d]],' % (
            block_count + 4, block_count, block_count + 5))
        tbfd.write('[%d,["hertz",{}],0,0,[%d,%d,null]],' % (
            block_count + 5, block_count + 4, block_count + 6))
        tbfd.write('[%d,["namedarg",{"value":%d}],0,0,[%d]],' % (
            block_count + 6, col_count + 1, block_count + 5))
        tbfd.write('[%d,["hidden",{}],0,0,[%d,' % (
            block_count + 7, block_count))

        block_count += 8;
        col_count += 1;

    # Finish off last note.
    tbfd.write('null]],')

    # Output a new action block and label to store the data.
    tbfd.write(
        '[%d,["action",{"collapsed":false}],100,200,[null,%d,%d,null]],' % (
            block_count, block_count + 1, block_count + 2))
    # No trailing comma in case there is no data, in which case, this
    # is the last block.
    tbfd.write('[%d,["text",{"value":"EVD"}],0,0,[%d]]' % (
        block_count + 1, block_count))

    block_count += 2;

    for lineno in range(len(line_data)):
        cols = line_data[lineno].split(',')
        
        # Write trailing comma to action here
        if lineno == 0:
            tbfd.write(',')
            prev_block = block_count - 2
        else:
            prev_block = block_count - col_count - 1

        tbfd.write('[%d,["nameddoArg",{"value":"action"}],0,0,[%d,' % (
            block_count, prev_block))

        ncols = 0;
        for i in range(len(cols)):

            if i in SKIPCOL:
                continue

            tbfd.write('%d,' % (block_count + 1 + ncols))
            ncols += 1

        # Last do block doesn't go anywhere
        if (lineno == len(line_data) - 1):
            tbfd.write('null]],')
        else:
            tbfd.write('%d]],' % (block_count + 1 + ncols))

        ncols = 0
        for i in range(len(cols)):

            if i in SKIPCOL:
                continue

            # append a comma to the previous line
            if ncols > 0:
                tbfd.write(',')

            print '%f' % (float(cols[i]) * 1000)
            tbfd.write('[%d,["number",{"value":%f}],0,0,[%d]]'
                       % (block_count + 1 + ncols, float(cols[i]) * 1000,
                          block_count))
            ncols += 1

        # No comma at the very end of the last line
        if (lineno < len(line_data) - 1):
            tbfd.write(',')

        block_count += 1 + ncols;

    tbfd.write(']')

    tbfd.close()

    return


if __name__ == '__main__':
    ini = from_csv_to_tb(sys.argv[1], sys.argv[2])
