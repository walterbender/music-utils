# music-utils

Several versions of a utility to parse CSV files into Music Block scripts.

The underlying assumption in these examples is that the CSV contains
opening, low, high, and closing values for a stock. These values are
converted into hertz.

Usage
-----

python csv2mb1.py input-csv-file output-musicblocks-file

Sample input:
[stocks.csv](https://raw.githubusercontent.com/walterbender/music-utils/master/stocks.csv)

Sample output:
[stocks.tb](https://raw.githubusercontent.com/walterbender/music-utils/master/stocks.tb)

[RUN LIVE](http://walterbender.github.io/musicblocks/?file=MusicBlocks_stockmarketreport.tb&run=true)
