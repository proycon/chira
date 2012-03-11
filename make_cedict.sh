#!/bin/bash
#Chinese Reading Assistant (Chira) - Dictionary Builder
#	by Maarten van Gompel (proycon)
#	proycon_AT_anaproy_DOT_nl
#	http://proylt.anaproy.nl
#	http://proycon.anaproy.nl
#
#	This program downloads and subsequently builds the chinese dictionary that 
#	is used by the application.
#
#	Licensed under the GNU Public License v3
#-----------------------------------------------------------------------------------
if [ ! -f "`which unzip`" ]; then
	echo "Error: unzip is required by this script. Please install (Ubuntu/Debian: sudo apt-get install unzip iconv)" >&2
	exit 1
fi 
if [ ! -f "`which wget`" ]; then
	echo "Error: wget is required by this script. Please install (Ubuntu/Debian: sudo apt-get install wget iconv)" >&2
	exit 1
fi 
rm -f cedict_ts.u8 > /dev/null 2> /dev/null
echo "Downloading CEDICT..."
wget http://www.mandarintools.com/download/cedictu8.zip
echo "Extracting..."
unzip cedictu8.zip
rm -f cedictu8.zip
#echo "Creating sorted dictionary for application (this may take a while!)..."
#./make_cedict.awk < cedict_ts.u8 | sort -rn > cedict_ts.u8.sorted
#rm -f cedict_ts.u8
echo "All done!"
