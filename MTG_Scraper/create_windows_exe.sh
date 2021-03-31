#!/bin/bash


mtg_windows='/home/edoardo/Dropbox/MTG_Scraper/'
cp *.txt $mtg_windows
cp *.csv $mtg_windows

#pyinstaller --onefile mtg_scraper.py
pyinstaller='/home/edoardo/.wine/drive_c/users/edoardo/Local\ Settings/Application Data/Programs/Python/Python36-32/Scripts/pyinstaller.exe'
wine $pyinstaller --onefile mtg_scraper.py

#cp dist/mtg_scraper $mtg_windows/'mtg_scraper.exe'



