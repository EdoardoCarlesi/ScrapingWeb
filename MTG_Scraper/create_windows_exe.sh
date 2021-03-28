#!/bin/bash


mtg_windows='/home/edoardo/Dropbox/MTG_Scraper/'
cp *.txt $mtg_windows
cp *.csv $mtg_windows

pyinstaller --onefile mtg_scraper.py

cp dist/mtg_scraper $mtg_windows/'mtg_scraper.exe'



