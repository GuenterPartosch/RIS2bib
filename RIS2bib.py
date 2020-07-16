#!/usr/bin/python
# -*- coding: utf-8 -*-

# RIS2bib.py
# (C) Günter Partosch, 2019/2010

# -------------------------------------------------------------
# Usage

# usage: RIS2bib.py [-h] [-a] [-o OUT_FILE] [-c CORRECTION_FILE] [-s SKIP] [-v]
#                   [-b] [-V]
#                   in_file
# 
# converts RIS files to .bib files [RIS2bib.py; Version: 1.7 (2020-07-16)]
# 
# Positional parameters:
#   in_file               name for input file; Default:
# 
# Optional parameters:
#   -h, --help            show this help message and exit
#   -a, --author          author of the program
#   -o OUT_FILE, --output OUT_FILE
#                         name for output file; Default: out-test.bib
#   -c CORRECTION_FILE, --correction CORRECTION_FILE
#                         name for a file with additional conversion rules;
#                         Default:
#   -s SKIP, --skip SKIP  skip BibTeX fields; Default: []
#   -v, --verbose         Flag: verbose output; Default: False
#   -b, --bibtexkeys      Flag: show the generated BibTeX keys; Default: False
#   -V, --version         version of the program


# =============================================================
# Messages
# --------
# 
# Fatal messages
# --------------
# input file" <input file> could not be opened; program terminated
# 
# Other error messages
# --------------------
# Correction file <correction file> could not be opened
# Line <line nr>: actual record not completed by 'ER  -'; skipped
# Line <line nr>: RIS type incorrect in '<line>'; 'GEN' supposed
# Line <line nr>: empty bibfield for <RIS type> <RIS key> in '<line>'; collected in 'note'
# Line <line nr>: unknown riskey for", <RIS type> <RIS key> in '<line>'
# 
# Informative messages
# --------------------
# File <correction file> with additional conversion rules read
# Generated BibTeX keys
# Program call: <program name> <arguments>
# Program finished


# =============================================================
# Examples
# --------
# 
# RIS2bib -h                                               [-h]
#    - help; show the options
# 
# RIS2bib inp.ris -o out.bib                               [-o]
#    - simple call
# 
# RIS2bib inp.ris -o out.bib -v                            [-o, -v]
#    - as above
#    - verbose output
# 
# RIS2bib inp.ris -o out.bib -b -v                         [-o, -b, -v]
#    - as above
#    - generated BibTeX keys are shown
# 
# RIS2bib inp2.ris -o out2.bib -v -c corr.py -b            [-o, -v, -c, -b]
#    - as above
#    - with some new conversion rules in corr.py;
#      the file corr.py must be in a special format, e.g.
# 
#      config["UNPB"]["SN"] = "isbn"
#      config["UNPB"]["U3"] = "note"
# 
# RIS2bib inp2.ris -o out2.bib -s ["note","abstract"] -v   [-o, -s, -v]
#    - the BibTeX fields "note" and "abstract" are skipped


# =============================================================
# The Preparation

# -------------------------------------------------------------
# Modules needed

import re                       # regular expressions
from unidecode import unidecode # mapping unicode charecters to ASCII
import sys                      # system calls
import platform                 # get OS informations
import argparse                 # argument parsing
import time                     # get time/date of file

# -------------------------------------------------------------
# program related infos

programname       = "RIS2bib.py"
programversion    = "1.7"
programdate       = "2020-07-16"
programauthor     = "Günter Partosch"
authorinstitution = "Justus-Liebig-Universität Gießen, Hochschulrechenzentrum"
authoremail       = "Guenter.Partosch@hrz.uni-giessen.de"
operatingsys      = platform.system()
call              = sys.argv

# -------------------------------------------------------------
# Initialize the conversion table

config            = {}
config["ADVS"]    = {"TY": "@audio"}         # ADVS, SLIDE, SOUND, VIDEO
config["ART"]     = {"TY": "@art"}           # Art work
config["BOOK"]    = {"TY": "@book"}          # Book
config["CHAP"]    = {"TY": "@inbook"}        # Chapter?
config["COMP"]    = {"TY": "@software"}      # Computer program
config["CONF"]    = {"TY": "@proceedings"}   # Conference proceeding
config["CPAPER"]  = {"TY": "@inproceedings"} # Conference paper
config["ELEC"]    = {"TY": "@online"}        # Electronic Citation
config["GEN"]     = {"TY": "@misc"}          # generic
config["ICOMM"]   = {"TY": "@online"}        # Internet communication
config["JOUR"]    = {"TY": "@article"}       # ABST, INPR, JFULL, JOUR
config["MANSCPT"] = {"TY": "@unpublished"}   # Manuscript
config["MUSIC"]   = {"TY": "@music"}         # Music score
config["NEWS"]    = {"TY": "@article"}       # Newspaper
config["PCOMM"]   = {"TY": "@letter"}        # Personal communication
config["THES"]    = {"TY": "@thesis"}        # Thesis/Dissertation
config["UNPB"]    = {"TY": "@unpublished"}   # Unpublished work

config["ADVS"]["A1"]    = "author"     # primary author
config["ADVS"]["A2"]    = "userd"      # Performers
config["ADVS"]["A3"]    = "editor"     # Series Editor
config["ADVS"]["A4"]    = ""           # Subsidiary Author / Translator
config["ADVS"]["AB"]    = "abstract"   # Abstract
config["ADVS"]["AD"]    = ""           # Author Address
config["ADVS"]["AN"]    = ""           # Accession Number
config["ADVS"]["AU"]    = "author"     # Author
config["ADVS"]["C1"]    = "usere"      # Cast
config["ADVS"]["C2"]    = ""           # Credits
config["ADVS"]["C3"]    = "userc"      # Size/Length
config["ADVS"]["C4"]    = "eventdate"  # Event Date
config["ADVS"]["C5"]    = "type"       # Format
config["ADVS"]["C7"]    = "eventtitle" # Event Title
config["ADVS"]["CA"]    = "usera"      # Caption
config["ADVS"]["CN"]    = ""           # Call Number
config["ADVS"]["CY"]    = "location"   # City
config["ADVS"]["DA"]    = "data"       # Date
config["ADVS"]["DB"]    = ""           # Name of Database
config["ADVS"]["DO"]    = "doi"        # DOI
config["ADVS"]["DP"]    = ""           # Database Provider
config["ADVS"]["ER"]    = ""           # End of Record
config["ADVS"]["ET"]    = "edition"    # Edition
config["ADVS"]["H1"]    = ""           # ?
config["ADVS"]["H2"]    = ""           # ?
config["ADVS"]["ID"]    = ""           # Reference ID
config["ADVS"]["J2"]    = ""           # Alternate Title
config["ADVS"]["KW"]    = "keywords"   # Keywords
config["ADVS"]["L1"]    = ""           # File Attachments
config["ADVS"]["L2"]    = ""           # ?
config["ADVS"]["L3"]    = ""           # ?
config["ADVS"]["L4"]    = ""           # Figure
config["ADVS"]["LA"]    = "language"   # Language
config["ADVS"]["LB"]    = "userb"      # Label
config["ADVS"]["M1"]    = "number"     # Number
config["ADVS"]["M3"]    = "type"       # Type
config["ADVS"]["N1"]    = "note"       # Notes
config["ADVS"]["N2"]    = "abstract"   # like AB
config["ADVS"]["NV"]    = ""           # Extent of Work
config["ADVS"]["OP"]    = "userf"      # Contents
config["ADVS"]["PB"]    = "publisher"  # Publisher
config["ADVS"]["PY"]    = "year"       # Year
config["ADVS"]["RN"]    = ""           # Research Notes
config["ADVS"]["SN"]    = "isbn"       # ISBN
config["ADVS"]["ST"]    = "shorttitle" # Short Title
config["ADVS"]["SV"]    = ""           # ?
config["ADVS"]["T1"]    = "title"      # Title
config["ADVS"]["T3"]    = "series"     # Series Title
config["ADVS"]["TA"]    = ""           # Translated Author
config["ADVS"]["TI"]    = "title"      # Title
config["ADVS"]["TT"]    = ""           # Translated Title
config["ADVS"]["U6"]    = ""           # like L1
config["ADVS"]["UR"]    = "url"        # URL
config["ADVS"]["VL"]    = "volume"     # Volume
config["ADVS"]["Y2"]    = "date"       # Date of last change
config["ADVS"]["Y3"]    = "urldate"    # Access Date

config["ART"]["A1"]     = "author"      # primary author
config["ART"]["A2"]     = "author"      # secondary author
config["ART"]["A3"]     = "author"      # tertiary author
config["ART"]["A4"]     = ""            # Subsidiary Author / Translator
config["ART"]["AB"]     = "abstract"    # Abstract
config["ART"]["AD"]     = ""            # Author Address
config["ART"]["AN"]     = ""            # Accession Number
config["ART"]["AU"]     = "author"      # Artist
config["ART"]["C1"]     = "venue"       # Place Published
config["ART"]["C2"]     = ""            # Year Published
config["ART"]["C3"]     = "userc"       # Size/Length
config["ART"]["C4"]     = "eventdate"   # Event Date
config["ART"]["C5"]     = ""            # Packaging Method
config["ART"]["C7"]     = "eventtitle"  # Event Title
config["ART"]["CA"]     = "usera"       # Caption
config["ART"]["CN"]     = ""            # Call Number
config["ART"]["CY"]     = "location"    # City
config["ART"]["DA"]     = "date"        # Date
config["ART"]["DB"]     = ""            # Name of Database
config["ART"]["DO"]     = "doi"         # DOI
config["ART"]["DP"]     = ""            # Database Provider
config["ART"]["ER"]     = ""            # End of Record
config["ART"]["ET"]     = "edition"     # Edition
config["ART"]["H1"]     = ""            # ?
config["ART"]["H2"]     = ""            # ?
config["ART"]["ID"]     = ""            # Reference ID
config["ART"]["J2"]     = ""            # Alternate Title
config["ART"]["KW"]     = "keywords"    # Keywords
config["ART"]["L1"]     = ""            # File Attachments
config["ART"]["L2"]     = ""            # ?
config["ART"]["L3"]     = ""            # ?
config["ART"]["L4"]     = ""            # Figure
config["ART"]["LA"]     = "language"    # Language
config["ART"]["LB"]     = "userb"       # Label
config["ART"]["M1"]     = "userc"       # Size
config["ART"]["M3"]     = "type"        # Type of Work
config["ART"]["N1"]     = "note"        # Notes
config["ART"]["N2"]     = "abstract"    # like AB
config["ART"]["PB"]     = "publisher"   # Publisher
config["ART"]["PY"]     = "year"        # Year
config["ART"]["RN"]     = ""            # Research Notes
config["ART"]["SP"]     = "description" # Description (add.)
config["ART"]["ST"]     = "shorttitle"  # Short Title
config["ART"]["SV"]     = ""            # ?
config["ART"]["T1"]     = "title"       # Title
config["ART"]["TA"]     = ""            # Translated Author
config["ART"]["TI"]     = "title"       # Title
config["ART"]["TT"]     = ""            # Translated Title
config["ART"]["U6"]     = ""            # like L1
config["ART"]["UR"]     = "url"         # URL
config["ART"]["Y2"]     = "date"        # Date of last change
config["ART"]["Y3"]     = "urldate"     # Access Date

config["BOOK"]["A1"]    = "author"       # primary author
config["BOOK"]["A2"]    = "editor"       # Series Editor
config["BOOK"]["A3"]    = "author"       # tertiary author
config["BOOK"]["A4"]    = "author"       # Translator
config["BOOK"]["A4"]    = ""             # Subsidiary Author / Translator
config["BOOK"]["AB"]    = "abstract"     # Abstract
config["BOOK"]["AD"]    = ""             # Author Address
config["BOOK"]["AN"]    = ""             # Accession Number
config["BOOK"]["AU"]    = "author"       # Author
config["BOOK"]["C1"]    = "venue"        # Place Published
config["BOOK"]["C2"]    = ""             # Year Published
config["BOOK"]["C3"]    = ""             # Proceedings Title
config["BOOK"]["C4"]    = "eventdate"    # Event Date
config["BOOK"]["C5"]    = ""             # Packaging Method
config["BOOK"]["C7"]    = "eventtitle"   # Event Title
config["BOOK"]["CA"]    = ""             # Caption
config["BOOK"]["CN"]    = ""             # Call Number
config["BOOK"]["CY"]    = "location"     # City
config["BOOK"]["DA"]    = "date"         # Date
config["BOOK"]["DB"]    = ""             # Name of Database
config["BOOK"]["DO"]    = "doi"          # DOI
config["BOOK"]["DP"]    = ""             # Database Provider
config["BOOK"]["ED"]    = "editor"       # Editor
config["BOOK"]["ER"]    = ""             # End of Record
config["BOOK"]["ET"]    = "edition"      # Edition
config["BOOK"]["H1"]    = ""             # ?
config["BOOK"]["H2"]    = ""             # ?
config["BOOK"]["ID"]    = ""             # Reference ID
config["BOOK"]["IN"]    = "organization" # institution
config["BOOK"]["IS"]    = "number"       # Issue
config["BOOK"]["J2"]    = ""             # Abbreviation
config["BOOK"]["KW"]    = "keywords"     # Keywords
config["BOOK"]["L1"]    = ""             # File Attachments
config["BOOK"]["L2"]    = ""             # ?
config["BOOK"]["L3"]    = ""             # ?
config["BOOK"]["L4"]    = ""             # Figure
config["BOOK"]["LA"]    = "language"     # Language
config["BOOK"]["LB"]    = ""             # Label
config["BOOK"]["M1"]    = ""             # Series Volume
config["BOOK"]["M3"]    = ""             # Type of Work
config["BOOK"]["M4"]    = ""             # Citavi
config["BOOK"]["N1"]    = "note"         # Notes
config["BOOK"]["N2"]    = "abstract"     # like AB
config["BOOK"]["NV"]    = "volumes"      # Number of Volumes
config["BOOK"]["OP"]    = ""             # Original Publication
config["BOOK"]["PB"]    = "publisher"    # Publisher
config["BOOK"]["PY"]    = "year"         # Year
config["BOOK"]["RN"]    = ""             # Research Notes
config["BOOK"]["RP"]    = ""             # Reprint Edition
config["BOOK"]["SE"]    = "pages"        # Pages
config["BOOK"]["SN"]    = "isbn"         # ISBN
config["BOOK"]["SP"]    = "pagetotal"    # Number of Pages
config["BOOK"]["ST"]    = "shorttitle"   # Short Title
config["BOOK"]["SV"]    = ""             # ?
config["BOOK"]["T1"]    = "title"        # Title
config["BOOK"]["T2"]    = "series"       # Series Title
config["BOOK"]["T4"]    = "subtitle"     # subtitle
config["BOOK"]["T5"]    = "titleaddon"   # titleaddon
config["BOOK"]["TA"]    = ""             # Translated Author
config["BOOK"]["TI"]    = "title"        # Title
config["BOOK"]["TS"]    = ""             # Title source
config["BOOK"]["TT"]    = ""             # Translated Title
config["BOOK"]["U3"]    = "note"         # Note
config["BOOK"]["U6"]    = ""             # like L1
config["BOOK"]["UR"]    = "url"          # URL
config["BOOK"]["VL"]    = "volume"       # Volume
config["BOOK"]["Y2"]    = "date"         # Date of last change
config["BOOK"]["Y3"]    = "urldate"      # Access Date

config["CHAP"]["A1"]    = "author"     # primary author
config["CHAP"]["A2"]    = "editor"     # Editor
config["CHAP"]["A3"]    = "author"     # tertiary author / Series Editor
config["CHAP"]["A4"]    = ""           # Subsidiary Author / Translator
config["CHAP"]["A4"]    = ""           # Translator
config["CHAP"]["AB"]    = "abstract"   # Abstract
config["CHAP"]["AD"]    = ""           # Author Address
config["CHAP"]["AN"]    = ""           # Accession Number
config["CHAP"]["AU"]    = "author"     # Author
config["CHAP"]["C1"]    = "venue"      # Place Published
config["CHAP"]["C2"]    = ""           # Year Published
config["CHAP"]["C3"]    = ""           # Title Prefix
config["CHAP"]["C4"]    = "eventdate"  # Event Date
config["CHAP"]["C5"]    = ""           # Packaging Method
config["CHAP"]["C7"]    = "eventtitle" # Event Title
config["CHAP"]["CA"]    = ""           # Caption
config["CHAP"]["CN"]    = ""           # Call Number
config["CHAP"]["CY"]    = "location"   # City
config["CHAP"]["DB"]    = ""           # Name of Database
config["CHAP"]["DO"]    = "doi"        # DOI
config["CHAP"]["DP"]    = ""           # Database Provider
config["CHAP"]["ED"]    = "editor"     # Editor
config["CHAP"]["EP"]    = "pages"      # end page
config["CHAP"]["ER"]    = ""           # End of Record
config["CHAP"]["ET"]    = "edition"    # Edition
config["CHAP"]["H1"]    = ""           # ?
config["CHAP"]["H2"]    = ""           # ?
config["CHAP"]["ID"]    = ""           # Reference ID
config["CHAP"]["IS"]    = "issue"      # Issue
config["CHAP"]["IS"]    = ""           # Number of Volumes
config["CHAP"]["J2"]    = ""           # Abbreviation
config["CHAP"]["KW"]    = "keywords"   # Keywords
config["CHAP"]["L1"]    = ""           # File Attachments
config["CHAP"]["L2"]    = ""           # ?
config["CHAP"]["L3"]    = ""           # ?
config["CHAP"]["L4"]    = ""           # Figure
config["CHAP"]["LA"]    = "language"   # Language
config["CHAP"]["LB"]    = ""           # Label
config["CHAP"]["M4"]    = ""           # Citavi
config["CHAP"]["N1"]    = "note"       # Notes
config["CHAP"]["N2"]    = "abstract"   # like AB
config["CHAP"]["OP"]    = ""           # Original Publication
config["CHAP"]["PB"]    = "publisher"  # Publisher
config["CHAP"]["PY"]    = "year"       # Year
config["CHAP"]["RI"]    = ""           # Reviewed Item
config["CHAP"]["RN"]    = ""           # Research Notes
config["CHAP"]["RP"]    = ""           # Reprint Edition
config["CHAP"]["SE"]    = "chapter"    # Chapter
config["CHAP"]["SN"]    = "isbn"       # ISBN
config["CHAP"]["SP"]    = "pages"      # Pages
config["CHAP"]["ST"]    = "shorttitle" # Short Title
config["CHAP"]["SV"]    = "number"     # Series Volume
config["CHAP"]["T1"]    = "title"      # Title
config["CHAP"]["T2"]    = "subtitle"   # Subtitle
config["CHAP"]["T3"]    = "series"     # Series Title
config["CHAP"]["T4"]    = "subtitle"   # subtitle
config["CHAP"]["T5"]    = "titleaddon" # titladdon
config["CHAP"]["TA"]    = ""           # Translated Author
config["CHAP"]["TI"]    = "title"      # Title
config["CHAP"]["TT"]    = ""           # Translated Title
config["CHAP"]["U6"]    = ""           # like L1
config["CHAP"]["UR"]    = "url"        # URL
config["CHAP"]["VL"]    = "volume"     # Volume
config["CHAP"]["Y2"]    = "date"       # Date of last change
config["CHAP"]["Y3"]    = "urldate"    # Access Date

config["COMP"]["A1"]    = "author"       # primary author
config["COMP"]["A2"]    = "author"       # secondary author
config["COMP"]["A3"]    = "author"       # tertiary author
config["COMP"]["A4"]    = "author"       # Involved Person
config["COMP"]["AB"]    = "abstract"     # Abstract
config["COMP"]["AD"]    = ""             # Author Address
config["COMP"]["AN"]    = ""             # Accession Number
config["COMP"]["AU"]    = "author"       # Programmer
config["COMP"]["C1"]    = "venue"        # Place Published
config["COMP"]["C2"]    = ""             # Year Published
config["COMP"]["C3"]    = ""             # Proceedings Title
config["COMP"]["C4"]    = "eventdate"    # Event Date
config["COMP"]["C5"]    = ""             # Packaging Method
config["COMP"]["C7"]    = "eventtitle"   # Event Title
config["COMP"]["CA"]    = ""             # Caption
config["COMP"]["CN"]    = ""             # Call Number
config["COMP"]["CY"]    = "location"     # City
config["COMP"]["DB"]    = ""             # Name of Database
config["COMP"]["DO"]    = "doi"          # DOI
config["COMP"]["DP"]    = ""             # Database Provider
config["COMP"]["ER"]    = ""             # End of Record
config["COMP"]["ET"]    = "edition"      # Edition
config["COMP"]["ET"]    = ""             # Version
config["COMP"]["H1"]    = ""             # ?
config["COMP"]["H2"]    = ""             # ?
config["COMP"]["ID"]    = ""             # Reference ID
config["COMP"]["IN"]    = "organization" # Institution
config["COMP"]["J2"]    = ""             # Alternate Title
config["COMP"]["KW"]    = "keywords"     # Keywords
config["COMP"]["L1"]    = ""             # File Attachments
config["COMP"]["L2"]    = ""             # ?
config["COMP"]["L3"]    = ""             # ?
config["COMP"]["L4"]    = ""             # Figure
config["COMP"]["LA"]    = "language"     # Language
config["COMP"]["LB"]    = ""             # Label
config["COMP"]["M1"]    = ""             # Computer
config["COMP"]["M3"]    = ""             # Type
config["COMP"]["M4"]    = ""             # Citavi
config["COMP"]["N1"]    = "note"         # Notes
config["COMP"]["N2"]    = "abstract"     # like AB
config["COMP"]["NV"]    = "volumes"      # Bandzahl
config["COMP"]["PB"]    = "publisher"    # Publisher
config["COMP"]["PY"]    = "year"         # Year
config["COMP"]["RN"]    = ""             # Research Notes
config["COMP"]["SN"]    = "isbn"         # ISBN
config["COMP"]["SP"]    = "pagetotal"    # Pages
config["COMP"]["ST"]    = "shorttitle"   # Short Title
config["COMP"]["SV"]    = ""             # ?
config["COMP"]["T1"]    = "title"        # Title
config["COMP"]["T2"]    = "series"       # Series Title
config["COMP"]["T4"]    = "subtitle"     # subtitle
config["COMP"]["T5"]    = "titleaddon"   # titleaddon
config["COMP"]["TA"]    = ""             # Translated Author
config["COMP"]["TI"]    = "title"        # Title
config["COMP"]["TT"]    = ""             # Translated Title
config["COMP"]["U3"]    = "note"         # Note
config["COMP"]["U6"]    = ""             # like L1
config["COMP"]["UR"]    = "url"          # URL
config["COMP"]["VL"]    = "volume"       # Volume Number
config["COMP"]["Y2"]    = "date"         # Date of last change
config["COMP"]["Y3"]    = "urldate"      # Access Date

config["CONF"]["A1"]    = "author"     # primary author
config["CONF"]["A2"]    = "editor"     # Editor
config["CONF"]["A3"]    = "author"     # tertiary author / Series Editor
config["CONF"]["A4"]    = ""           # Sponsor
config["CONF"]["AB"]    = "abstract"   # Abstract
config["CONF"]["AD"]    = ""           # Author Address
config["CONF"]["AN"]    = ""           # Accession Number
config["CONF"]["AU"]    = "author"     # Author
config["CONF"]["C1"]    = "venue"      # Place Published
config["CONF"]["C2"]    = ""           # Year Published
config["CONF"]["C3"]    = ""           # Proceedings Title
config["CONF"]["C4"]    = "eventdate"  # Event Date
config["CONF"]["C5"]    = ""           # Packaging Method
config["CONF"]["C7"]    = "eventtitle" # Event Title
config["CONF"]["CA"]    = ""           # Caption
config["CONF"]["CN"]    = ""           # Call Number
config["CONF"]["CY"]    = "location"   # Conference Location
config["CONF"]["DA"]    = "date"       # Date
config["CONF"]["DB"]    = ""           # Name of Database
config["CONF"]["DO"]    = "doi"        # DOI
config["CONF"]["DP"]    = ""           # Database Provider
config["CONF"]["ER"]    = ""           # End of Record
config["CONF"]["ET"]    = "edition"    # Edition
config["CONF"]["H1"]    = ""           # ?
config["CONF"]["H2"]    = ""           # ?
config["CONF"]["ID"]    = ""           # Reference ID
config["CONF"]["IS"]    = "number"     # Zusatztitel
config["CONF"]["JA"]    = ""           # Zusatztitel
config["CONF"]["KW"]    = "keywords"   # Keywords
config["CONF"]["L1"]    = ""           # File Attachments
config["CONF"]["L2"]    = ""           # ?
config["CONF"]["L3"]    = ""           # ?
config["CONF"]["L4"]    = ""           # Figure
config["CONF"]["LA"]    = "language"   # Language
config["CONF"]["LB"]    = ""           # Label
config["CONF"]["M1"]    = ""           # Issue
config["CONF"]["M4"]    = ""           # Citavi
config["CONF"]["N1"]    = "note"       # Notes
config["CONF"]["N2"]    = "abstract"   # like AB
config["CONF"]["NV"]    = "volumes"    # Number of Volumes
config["CONF"]["PB"]    = "publisher"  # Publisher
config["CONF"]["PY"]    = "year"       # Year of Conference
config["CONF"]["RN"]    = ""           # Research Notes
config["CONF"]["SN"]    = "isbn"       # ISBN
config["CONF"]["SP"]    = "pagetotal"  # Pages
config["CONF"]["ST"]    = "shorttitle" # Short Title
config["CONF"]["SV"]    = ""           # ?
config["CONF"]["T1"]    = "title"      # Title
config["CONF"]["T2"]    = "eventtitle" # Event Name
config["CONF"]["T3"]    = "series"     # Series Title
config["CONF"]["T4"]    = "subtitle"   # subtitle
config["CONF"]["T5"]    = "titleaddon" # titleaddon
config["CONF"]["TA"]    = ""           # Translated Author
config["CONF"]["TI"]    = "title"      # Title
config["CONF"]["TT"]    = ""           # Translated Title
config["CONF"]["U6"]    = ""           # like L1
config["CONF"]["UR"]    = "url"        # URL
config["CONF"]["VL"]    = "volume"     # Volume
config["CONF"]["Y2"]    = "date"       # Date of last change
config["CONF"]["Y3"]    = "urldate"    # Access Date

config["CPAPER"]["A1"]  = "author"       # primary author
config["CPAPER"]["A2"]  = "editor"       # Editor
config["CPAPER"]["A3"]  = "author"       # tertiary author
config["CPAPER"]["A4"]  = ""             # Subsidiary Author / Translator
config["CPAPER"]["AB"]  = "abstract"     # Abstract
config["CPAPER"]["AD"]  = ""             # Author Address
config["CPAPER"]["AN"]  = ""             # Accession Number
config["CPAPER"]["AU"]  = "author"       # Author
config["CPAPER"]["C1"]  = "venue"        # Place Published
config["CPAPER"]["C2"]  = ""             # Year Published
config["CPAPER"]["C3"]  = ""             # Proceedings Title
config["CPAPER"]["C4"]  = "eventdate"    # Event Date
config["CPAPER"]["C5"]  = ""             # Packaging Method
config["CPAPER"]["C7"]  = "eventtitle"   # Event Title
config["CPAPER"]["CA"]  = ""             # Caption
config["CPAPER"]["CY"]  = "location"     # Conference Location
config["CPAPER"]["DA"]  = ""             # Date
config["CPAPER"]["DB"]  = ""             # Name of Database
config["CPAPER"]["DO"]  = "doi"          # DOI
config["CPAPER"]["DP"]  = ""             # Database Provider
config["CPAPER"]["ED"]  = "editor"       # Editor?"CY"
config["CPAPER"]["EP"]  = "pages"        # End Page
config["CPAPER"]["ER"]  = ""             # End of Record
config["CPAPER"]["ET"]  = "edition"      # Edition
config["CPAPER"]["H1"]  = ""             # ?
config["CPAPER"]["H2"]  = ""             # ?
config["CPAPER"]["ID"]  = ""             # Reference ID
config["CPAPER"]["IN"]  = "organization" # Heftnummer
config["CPAPER"]["IS"]  = "number"       # Heftnummer
config["CPAPER"]["KW"]  = "keywords"     # Keywords
config["CPAPER"]["L1"]  = ""             # File Attachments
config["CPAPER"]["L2"]  = ""             # ?
config["CPAPER"]["L3"]  = ""             # ?
config["CPAPER"]["L4"]  = ""             # Figure
config["CPAPER"]["LA"]  = "language"     # Language
config["CPAPER"]["LB"]  = ""             # Label
config["CPAPER"]["M3"]  = ""             # Type of Work
config["CPAPER"]["M4"]  = ""             # Citavi
config["CPAPER"]["N1"]  = "note"         # Notes
config["CPAPER"]["N2"]  = "abstract"     # like AB
config["CPAPER"]["PB"]  = "publisher"    # Publisher
config["CPAPER"]["PY"]  = "year"         # Year
config["CPAPER"]["RN"]  = ""             # Research Notes
config["CPAPER"]["SN"]  = "isbn"         # ISBN
config["CPAPER"]["SP"]  = "pages"        # Pages
config["CPAPER"]["SP"]  = "pages"        # Start Page
config["CPAPER"]["ST"]  = "shorttitle"   # Short Title
config["CPAPER"]["T1"]  = "title"        # Title
config["CPAPER"]["T2"]  = ""             # Conference Name
config["CPAPER"]["T2"]  = "subtitle"     # Subtitle
config["CPAPER"]["T3"]  = "series"       # series
config["CPAPER"]["T4"]  = "subtitle"     # subtitle 
config["CPAPER"]["T5"]  = "titleaddon"   # titleaddon
config["CPAPER"]["TA"]  = ""             # Translated Author
config["CPAPER"]["TI"]  = "title"        # Title
config["CPAPER"]["TT"]  = ""             # Translated Title
config["CPAPER"]["U6"]  = ""             # like L1
config["CPAPER"]["UR"]  = "url"          # URL
config["CPAPER"]["VL"]  = "volume"       # Volume
config["CPAPER"]["Y2"]  = "date"         # Date of last change
config["CPAPER"]["Y3"]  = "urldate"      # Access Date

config["ELEC"]["A1"]    = "author"       # primary author
config["ELEC"]["A2"]    = "editor"       # Series Editor
config["ELEC"]["A3"]    = "author"       # tertiary author
config["ELEC"]["A4"]    = ""             # Series Editor
config["ELEC"]["A4"]    = ""             # Subsidiary Author / Translator
config["ELEC"]["AB"]    = "abstract"     # Abstract
config["ELEC"]["AD"]    = ""             # Author Address
config["ELEC"]["AN"]    = ""             # Accession Number
config["ELEC"]["AU"]    = "author"       # Author
config["ELEC"]["C1"]    = "venue"        # Place Published
config["ELEC"]["C2"]    = ""             # Year Published
config["ELEC"]["C2"]    = "urldate"      # Date Cited
config["ELEC"]["C3"]    = ""             # Proceedings Title
config["ELEC"]["C4"]    = "eventdate"    # Event Date
config["ELEC"]["C5"]    = ""             # Packaging Method
config["ELEC"]["C7"]    = "eventtitle"   # Event Title
config["ELEC"]["CA"]    = ""             # Caption
config["ELEC"]["CN"]    = ""             # Call Number
config["ELEC"]["CY"]    = "location"     # City
config["ELEC"]["DA"]    = "date"         # Last Update Date
config["ELEC"]["DB"]    = ""             # Name of Database
config["ELEC"]["DO"]    = "doi"          # DOI
config["ELEC"]["DP"]    = ""             # Database Provider
config["ELEC"]["ER"]    = ""             # End of Record
config["ELEC"]["ET"]    = "edition"      # Edition
config["ELEC"]["H1"]    = ""             # ?
config["ELEC"]["H2"]    = ""             # ?
config["ELEC"]["ID"]    = ""             # Reference ID
config["ELEC"]["J2"]    = ""             # Alternate Title
config["ELEC"]["KW"]    = "keywords"     # Keywords
config["ELEC"]["L1"]    = ""             # File Attachments
config["ELEC"]["L2"]    = ""             # ?
config["ELEC"]["L3"]    = ""             # ?
config["ELEC"]["L4"]    = ""             # Figure
config["ELEC"]["LA"]    = "language"     # Language
config["ELEC"]["LB"]    = ""             # Label
config["ELEC"]["M1"]    = "urldate"      # Access Date
config["ELEC"]["M3"]    = "howpublished" # Type of Medium"CY"
config["ELEC"]["N1"]    = "note"         # Notes
config["ELEC"]["N2"]    = "abstract"     # like AB
config["ELEC"]["OP"]    = ""             # Contents
config["ELEC"]["PB"]    = "publisher"    # Publisher
config["ELEC"]["PY"]    = "year"         # Year
config["ELEC"]["RN"]    = ""             # Research Notes
config["ELEC"]["SN"]    = "isbn"         # ISBN
config["ELEC"]["SP"]    = ""             # Description
config["ELEC"]["ST"]    = "shorttitle"   # Short Title
config["ELEC"]["SV"]    = ""             # ?
config["ELEC"]["T1"]    = "title"        # Title
config["ELEC"]["T2"]    = "series"       # Series Title
config["ELEC"]["TA"]    = ""             # Translated Author
config["ELEC"]["TI"]    = "title"        # Title
config["ELEC"]["TT"]    = ""             # Translated Title
config["ELEC"]["U6"]    = ""             # like L1
config["ELEC"]["UR"]    = "url"          # URL
config["ELEC"]["VL"]    = ""             # Access Year
config["ELEC"]["Y2"]    = "date"         # Date of last change
config["ELEC"]["Y3"]    = "urldate"      # Access Date

config["GEN"]["A1"]     = "author"       # primary author
config["GEN"]["A2"]     = "author"       # secondary author
config["GEN"]["A3"]     = "author"       # tertiary author
config["GEN"]["A4"]     = "author"       # Involved Person
config["GEN"]["AB"]     = "abstract"     # Abstract
config["GEN"]["AD"]     = ""             # Author Address
config["GEN"]["AN"]     = ""             # Accession Number
config["GEN"]["AU"]     = "author"       # Author
config["GEN"]["C1"]     = ""             # Custom 1
config["GEN"]["C2"]     = ""             # Custom 2
config["GEN"]["C3"]     = ""             # Custom 3
config["GEN"]["C4"]     = ""             # Custom 4
config["GEN"]["C5"]     = ""             # Custom 5
config["GEN"]["C6"]     = ""             # Custom 6
config["GEN"]["C7"]     = "eventtitle"   # Event Title
config["GEN"]["C8"]     = ""             # Custom 8
config["GEN"]["CA"]     = ""             # Caption
config["GEN"]["CN"]     = ""             # Call Number
config["GEN"]["CY"]     = "location"     # Place Published
config["GEN"]["DA"]     = "date"         # Date
config["GEN"]["DB"]     = ""             # Name of Database
config["GEN"]["DO"]     = "doi"          # DOI
config["GEN"]["DP"]     = ""             # Database Provider
config["GEN"]["ED"]     = "editor"       # Editor
config["GEN"]["ER"]     = ""             # End of Record
config["GEN"]["ET"]     = "edition"      # Edition
config["GEN"]["H1"]     = ""             # ?
config["GEN"]["H2"]     = ""             # ?
config["GEN"]["ID"]     = ""             # Reference ID
config["GEN"]["IN"]     = "organization" # institution
config["GEN"]["IS"]     = "issue"        # Issue
config["GEN"]["J2"]     = ""             # Alternate Title
config["GEN"]["JF"]     = "series"       # Zeitschrift
config["GEN"]["KW"]     = "keywords"     # Keywords
config["GEN"]["L1"]     = ""             # File Attachments
config["GEN"]["L2"]     = ""             # ?
config["GEN"]["L3"]     = ""             # ?
config["GEN"]["L4"]     = ""             # Figure
config["GEN"]["LA"]     = "language"     # Language
config["GEN"]["LB"]     = ""             # Label
config["GEN"]["M1"]     = "number"       # Number
config["GEN"]["M3"]     = "type"         # Type of Work
config["GEN"]["M4"]     = ""             # Citavi
config["GEN"]["N1"]     = "note"         # Notes
config["GEN"]["N2"]     = "abstract"     # like AB
config["GEN"]["NV"]     = "volumes"      # Number of Volumes
config["GEN"]["OP"]     = ""             # Original Publication
config["GEN"]["PB"]     = "publisher"    # Publisher
config["GEN"]["PY"]     = "year"         # Year
config["GEN"]["RI"]     = ""             # Reviewed Item
config["GEN"]["RN"]     = ""             # Research Notes
config["GEN"]["RP"]     = ""             # Reprint Edition
config["GEN"]["SE"]     = ""             # Section
config["GEN"]["SN"]     = "isbn"         # ISBN/ISSN
config["GEN"]["SP"]     = "pages"        # Pages
config["GEN"]["ST"]     = "shorttitle"   # Short Title
config["GEN"]["SV"]     = ""             # ?
config["GEN"]["T1"]     = "title"        # Title
config["GEN"]["T2"]     = "series"       # Secondary Title
config["GEN"]["T3"]     = ""             # Tertiary Title
config["GEN"]["T4"]     = "subtitle"     # subtitle
config["GEN"]["T5"]     = "titleaddon"   # titleaddon
config["GEN"]["TA"]     = ""             # Translated Author
config["GEN"]["TI"]     = "title"        # Title
config["GEN"]["TT"]     = ""             # Translated Title
config["GEN"]["U3"]     = "note"         # Note
config["GEN"]["U6"]     = ""             # like L1
config["GEN"]["UR"]     = "url"          # URL
config["GEN"]["VL"]     = "volume"       # Volume
config["GEN"]["Y2"]     = "date"         # Date of last change
config["GEN"]["Y3"]     = "urldate"      # Access Date

config["ICOMM"]["A1"]   = "author"       # primary author
config["ICOMM"]["A2"]   = "editor"       # Recipient
config["ICOMM"]["A3"]   = "author"       # tertiary author
config["ICOMM"]["A4"]   = ""             # Subsidiary Author / Translator
config["ICOMM"]["AB"]   = "abstract"     # Abstract
config["ICOMM"]["AD"]   = ""             # Author Address
config["ICOMM"]["AN"]   = ""             # Accession Number
config["ICOMM"]["AU"]   = "author"       # Author
config["ICOMM"]["C1"]   = "venue"        # Place Published
config["ICOMM"]["C2"]   = ""             # Recieipients EMail
config["ICOMM"]["C3"]   = ""             # Proceedings Title
config["ICOMM"]["C4"]   = "eventdate"    # Event Date
config["ICOMM"]["C5"]   = ""             # Packaging Method
config["ICOMM"]["C7"]   = "eventtitle"   # Event Title
config["ICOMM"]["CA"]   = ""             # Caption
config["ICOMM"]["CN"]   = ""             # Call Number
config["ICOMM"]["CY"]   = "location"     # City
config["ICOMM"]["DA"]   = "date"         # Date
config["ICOMM"]["DB"]   = ""             # Name of Database
config["ICOMM"]["DO"]   = "doi"          # DOI
config["ICOMM"]["DP"]   = ""             # Database Provider
config["ICOMM"]["ER"]   = ""             # End of Record
config["ICOMM"]["ET"]   = "version"      # Description?
config["ICOMM"]["H1"]   = ""             # ?
config["ICOMM"]["H2"]   = ""             # ?
config["ICOMM"]["ID"]   = ""             # Reference ID
config["ICOMM"]["IN"]   = "organization" # Institution
config["ICOMM"]["IS"]   = "number"       # number
config["ICOMM"]["J2"]   = ""             # Abbreviation
config["ICOMM"]["KW"]   = "keywords"     # Keywords
config["ICOMM"]["L1"]   = ""             # File Attachments
config["ICOMM"]["L2"]   = ""             # ?
config["ICOMM"]["L3"]   = ""             # ?
config["ICOMM"]["L4"]   = ""             # Figure
config["ICOMM"]["LA"]   = "language"     # Language
config["ICOMM"]["LB"]   = ""             # Label
config["ICOMM"]["M1"]   = ""             # Folio Number
config["ICOMM"]["M3"]   = "type"         # Type
config["ICOMM"]["M4"]   = ""             # Citavi
config["ICOMM"]["N1"]   = "note"         # Notes
config["ICOMM"]["N2"]   = "abstract"     # like AB
config["ICOMM"]["NV"]   = ""             # Communication Number
config["ICOMM"]["PB"]   = "publisher"    # Publisher
config["ICOMM"]["PY"]   = "year"         # Year
config["ICOMM"]["RN"]   = ""             # Research Notes
config["ICOMM"]["SN"]   = "isbn"         # ISBN
config["ICOMM"]["SP"]   = "pagetotal"    # Pages
config["ICOMM"]["ST"]   = "shorttitle"   # Short Title
config["ICOMM"]["SV"]   = ""             # ?
config["ICOMM"]["T1"]   = "title"        # Title
config["ICOMM"]["T2"]   = "subtitle"     # subtitle
config["ICOMM"]["T3"]   = "series"       # series
config["ICOMM"]["T5"]   = "titleaddon"   # Titleaddon
config["ICOMM"]["TA"]   = ""             # Translated Author
config["ICOMM"]["TI"]   = "title"        # Title
config["ICOMM"]["TT"]   = ""             # Translated Title
config["ICOMM"]["U6"]   = ""             # like L1
config["ICOMM"]["UR"]   = "url"          # URL
config["ICOMM"]["VL"]   = "volume"       # Titleaddon?
config["ICOMM"]["Y2"]   = "date"         # Date of last change
config["ICOMM"]["Y3"]   = "urldate"      # Access Date

config["JOUR"]["A1"]    = "author"       # primary author
config["JOUR"]["A2"]    = "publisher"    # secondary author
config["JOUR"]["A3"]    = "author"       # tertiary author
config["JOUR"]["A4"]    = ""             # Subsidiary Author / Translator
config["JOUR"]["AB"]    = "abstract"     # Abstract
config["JOUR"]["AD"]    = ""             # Author Address
config["JOUR"]["AN"]    = ""             # Accession Number
config["JOUR"]["AU"]    = "author"       # Author
config["JOUR"]["C1"]    = "venue"        # Place Published
config["JOUR"]["C2"]    = ""             # PMCID
config["JOUR"]["C3"]    = ""             # Proceedings Title
config["JOUR"]["C4"]    = "eventdate"    # Event Date
config["JOUR"]["C5"]    = ""             # Packaging Method
config["JOUR"]["C6"]    = ""             # NIHMSID
config["JOUR"]["C7"]    = ""             # Article Number
config["JOUR"]["CA"]    = ""             # Caption
config["JOUR"]["CN"]    = ""             # Call Number
config["JOUR"]["CY"]    = "location"     # 
config["JOUR"]["DA"]    = "date"         # Date
config["JOUR"]["DB"]    = ""             # Name of Database
config["JOUR"]["DO"]    = "doi"          # DOI
config["JOUR"]["DP"]    = ""             # Database Provider
config["JOUR"]["EP"]    = "pages"        # End Page
config["JOUR"]["ER"]    = ""             # End of Record
config["JOUR"]["ET"]    = ""             # Epub Date
config["JOUR"]["H1"]    = ""             # ?
config["JOUR"]["H2"]    = ""             # ?
config["JOUR"]["ID"]    = ""             # Reference ID
config["JOUR"]["IN"]    = "organization" # 
config["JOUR"]["IS"]    = "number"       # Issue
config["JOUR"]["J2"]    = ""             # Alternate Journal
config["JOUR"]["JA"]    = "series"       # 
config["JOUR"]["JF"]    = "journaltitle" # Journaltitle
config["JOUR"]["KW"]    = "keywords"     # Keywords
config["JOUR"]["L1"]    = ""             # File Attachments
config["JOUR"]["L2"]    = ""             # ?
config["JOUR"]["L3"]    = ""             # ?
config["JOUR"]["L4"]    = ""             # Figure
config["JOUR"]["LA"]    = "language"     # Language
config["JOUR"]["LB"]    = ""             # Label
config["JOUR"]["M2"]    = ""             # Start Page
config["JOUR"]["M3"]    = "howpublished" # Type of Article
config["JOUR"]["M4"]    = ""             # 
config["JOUR"]["N1"]    = "note"         # Notes
config["JOUR"]["N2"]    = "abstract"     # like AB
config["JOUR"]["OP"]    = ""             # Original Publication
config["JOUR"]["PB"]    = "publisher"    # publisher
config["JOUR"]["PY"]    = "year"         # Year
config["JOUR"]["RI"]    = ""             # Reviewed Item
config["JOUR"]["RN"]    = ""             # Research Notes
config["JOUR"]["RP"]    = ""             # Reprint Edition
config["JOUR"]["SN"]    = "issn"         # ISSN
config["JOUR"]["SP"]    = "pages"        # Start Page
config["JOUR"]["ST"]    = "shorttitle"   # Short Title
config["JOUR"]["SV"]    = ""             # ?
config["JOUR"]["T1"]    = "title"        # Title
config["JOUR"]["T2"]    = ""             # Journal
config["JOUR"]["T3"]    = "journaltitle" # Citavi
config["JOUR"]["T4"]    = "subtitle"     # subtitle
config["JOUR"]["T5"]    = "titleaddon"   # titleaddonJOUR
config["JOUR"]["TA"]    = ""             # Translated Author
config["JOUR"]["TI"]    = "title"        # Title
config["JOUR"]["TT"]    = ""             # Translated Title
config["JOUR"]["U3"]    = "note"         # Note
config["JOUR"]["U6"]    = ""             # like L1
config["JOUR"]["UR"]    = "url"          # URL
config["JOUR"]["VL"]    = "volume"       # Volume
config["JOUR"]["Y2"]    = "date"         # Date of last change
config["JOUR"]["Y3"]    = "urldate"      # Access Date

config["MANSCPT"]["A1"] = "author"       # primary author
config["MANSCPT"]["A2"] = "editor"       # A2
config["MANSCPT"]["A3"] = "author"       # tertiary author
config["MANSCPT"]["A4"] = ""             # Subsidiary Author / Translator
config["MANSCPT"]["AB"] = "abstract"     # Abstract
config["MANSCPT"]["AD"] = ""             # Author Address
config["MANSCPT"]["AN"] = ""             # Accession Number
config["MANSCPT"]["AU"] = "author"       # Author
config["MANSCPT"]["C1"] = "venue"        # Place Published
config["MANSCPT"]["C2"] = ""             # Year Published
config["MANSCPT"]["C3"] = ""             # Proceedings Title
config["MANSCPT"]["C4"] = "eventdate"    # Event Date
config["MANSCPT"]["C5"] = ""             # Packaging Method
config["MANSCPT"]["C7"] = "eventtitle"   # Event Title
config["MANSCPT"]["CA"] = ""             # Caption
config["MANSCPT"]["CN"] = ""             # Call Number
config["MANSCPT"]["CY"] = "location"     # City
config["MANSCPT"]["DA"] = "date"         # Date
config["MANSCPT"]["DB"] = ""             # Name of Database
config["MANSCPT"]["DO"] = "doi"          # DOI
config["MANSCPT"]["DP"] = ""             # Database Provider
config["MANSCPT"]["ED"] = "editor"       # Editor
config["MANSCPT"]["ER"] = ""             # End of Record
config["MANSCPT"]["ET"] = ""             # Description of Material
config["MANSCPT"]["H1"] = ""             # ?
config["MANSCPT"]["H2"] = ""             # ?
config["MANSCPT"]["ID"] = ""             # Reference ID
config["MANSCPT"]["J2"] = ""             # Abbreviation
config["MANSCPT"]["KW"] = "keywords"     # Keywords
config["MANSCPT"]["L1"] = ""             # File Attachments
config["MANSCPT"]["L2"] = ""             # ?
config["MANSCPT"]["L3"] = ""             # ?
config["MANSCPT"]["L4"] = ""             # Figure
config["MANSCPT"]["LA"] = "language"     # Language
config["MANSCPT"]["LB"] = ""             # Label
config["MANSCPT"]["M1"] = ""             # Folio Number
config["MANSCPT"]["M3"] = "type"         # Type of Work
config["MANSCPT"]["N1"] = "note"         # Notes
config["MANSCPT"]["N2"] = "abstract"     # like AB
config["MANSCPT"]["NV"] = "number"       # Manuscript Number
config["MANSCPT"]["PB"] = "organization" # Library/Archive
config["MANSCPT"]["PY"] = "year"         # Year
config["MANSCPT"]["RN"] = ""             # Research Notes
config["MANSCPT"]["RP"] = ""             # Reprint Edition
config["MANSCPT"]["SE"] = "pages"        # Start Page?
config["MANSCPT"]["SP"] = "pagetotal"    # Pages
config["MANSCPT"]["ST"] = "shorttitle"   # Short Title
config["MANSCPT"]["SV"] = ""             # ?
config["MANSCPT"]["T1"] = "title"        # Titleline 
config["MANSCPT"]["T2"] = "series"       # Collection Title
config["MANSCPT"]["T4"] = "subtitle"     # Subtitle
config["MANSCPT"]["T5"] = "titleaddon"   # titleaddon
config["MANSCPT"]["TA"] = ""             # Translated Author
config["MANSCPT"]["TI"] = "title"        # Title
config["MANSCPT"]["TT"] = ""             # Translated Title
config["MANSCPT"]["U6"] = ""             # like L1
config["MANSCPT"]["UR"] = "url"          # URL
config["MANSCPT"]["VL"] = ""             # Volume/Storage Container
config["MANSCPT"]["Y2"] = "date"         # Date of last change
config["MANSCPT"]["Y3"] = "urldate"      # Access Date

config["MUSIC"]["A1"]   = "author"      # primary author
config["MUSIC"]["A2"]   = "author"      # secondary author
config["MUSIC"]["A2"]   = "editor"      # Editor
config["MUSIC"]["A3"]   = ""            # Series Editor
config["MUSIC"]["A4"]   = "producer"    # Producer (add.)
config["MUSIC"]["AB"]   = "abstract"    # Abstract
config["MUSIC"]["AD"]   = ""            # Author Address
config["MUSIC"]["AN"]   = ""            # Accession Number
config["MUSIC"]["AU"]   = "author"      # Composer
config["MUSIC"]["C1"]   = "type"        # Format of Music
config["MUSIC"]["C2"]   = "composition" # Form of Composition (add.)
config["MUSIC"]["C3"]   = ""            # Music Parts
config["MUSIC"]["C4"]   = "audience"    # Target Audience (add.)
config["MUSIC"]["C5"]   = ""            # Accompanying Matter
config["MUSIC"]["C7"]   = "eventtitle"  # Event Title
config["MUSIC"]["CA"]   = "usera"       # Caption
config["MUSIC"]["CN"]   = ""            # Call Number
config["MUSIC"]["CY"]   = "location"    # Place Published
config["MUSIC"]["DA"]   = "date"        # Date
config["MUSIC"]["DB"]   = ""            # Name of Database
config["MUSIC"]["DO"]   = "doi"         # DOI
config["MUSIC"]["DP"]   = ""            # Database Provider
config["MUSIC"]["ER"]   = ""            # End of Record
config["MUSIC"]["ET"]   = "edition"     # Edition
config["MUSIC"]["H1"]   = ""            # ?
config["MUSIC"]["H2"]   = ""            # ?
config["MUSIC"]["ID"]   = ""            # Reference ID
config["MUSIC"]["KW"]   = "keywords"    # Keywords
config["MUSIC"]["L1"]   = ""            # File Attachments
config["MUSIC"]["L2"]   = ""            # ?
config["MUSIC"]["L3"]   = ""            # ?
config["MUSIC"]["L4"]   = ""            # Figure
config["MUSIC"]["LA"]   = "language"    # Language
config["MUSIC"]["LB"]   = "userb"       # Label
config["MUSIC"]["M3"]   = ""            # Form of Item
config["MUSIC"]["N1"]   = "note"        # Notes
config["MUSIC"]["N2"]   = "abstract"    # like AB
config["MUSIC"]["NV"]   = "volumes"     # Number of Volumes
config["MUSIC"]["OP"]   = ""            # Original Publication
config["MUSIC"]["PB"]   = "publisher"   # Publisher
config["MUSIC"]["PY"]   = "year"        # Year
config["MUSIC"]["RN"]   = ""            # Research Notes
config["MUSIC"]["RP"]   = ""            # Reprint Edition
config["MUSIC"]["SE"]   = ""            # Section
config["MUSIC"]["SN"]   = "issn"        # ISSN
config["MUSIC"]["SP"]   = "pages"       # Pages
config["MUSIC"]["ST"]   = "shorttitle"  # Short Title
config["MUSIC"]["SV"]   = ""            # ?
config["MUSIC"]["T1"]   = "title"       # Title
config["MUSIC"]["T2"]   = "album"       # Album Title (add.)
config["MUSIC"]["T3"]   = "series"      # Series Title
config["MUSIC"]["T4"]   = "subtitle"    # subtitle
config["MUSIC"]["T5"]   = "titleaddon"  # titleaddon
config["MUSIC"]["TA"]   = ""            # Translated Author
config["MUSIC"]["TI"]   = "title"       # Title
config["MUSIC"]["TT"]   = ""            # Translated Title
config["MUSIC"]["U6"]   = ""            # like L1
config["MUSIC"]["UR"]   = "url"         # URL
config["MUSIC"]["VL"]   = "volume"      # Volume
config["MUSIC"]["Y2"]   = "date"        # Date of last change
config["MUSIC"]["Y3"]   = "urldate"     # Access Date

config["NEWS"]["A1"]    = "author"       # primary author
config["NEWS"]["A2"]    = "author"       # secondary author
config["NEWS"]["A3"]    = "author"       # tertiary author
config["NEWS"]["AB"]    = "abstract"     # Abstract
config["NEWS"]["AD"]    = ""             # Author Address
config["NEWS"]["AN"]    = ""             # Accession Number
config["NEWS"]["AU"]    = "author"       # Reporter
config["NEWS"]["C1"]    = "venue"        # Place Published
config["NEWS"]["C2"]    = "number"       # Issue
config["NEWS"]["C3"]    = ""             # Proceedings Title
config["NEWS"]["C4"]    = "eventdate"    # Event Date
config["NEWS"]["C5"]    = ""             # Packaging Method
config["NEWS"]["C7"]    = "eventtitle"   # Event Title
config["NEWS"]["CA"]    = ""             # Caption
config["NEWS"]["CN"]    = ""             # Call Number
config["NEWS"]["CY"]    = "location"     # City
config["NEWS"]["DA"]    = "date"         # Date
config["NEWS"]["DB"]    = ""             # Name of Database
config["NEWS"]["DO"]    = "doi"          # DOI
config["NEWS"]["DP"]    = ""             # Database Provider
config["NEWS"]["EP"]    = "pages"        # End Page
config["NEWS"]["ER"]    = ""             # End of Record
config["NEWS"]["ET"]    = "edition"      # Edition
config["NEWS"]["H1"]    = ""             # ?
config["NEWS"]["H2"]    = ""             # ?
config["NEWS"]["ID"]    = ""             # Reference ID
config["NEWS"]["IS"]    = "number"       # Issue
config["NEWS"]["JF"]    = "journaltitle" # journaltitle
config["NEWS"]["KW"]    = "keywords"     # Keywords
config["NEWS"]["L1"]    = ""             # Figure
config["NEWS"]["L2"]    = ""             # ?
config["NEWS"]["L3"]    = ""             # ?
config["NEWS"]["L4"]    = ""             # File Attachments
config["NEWS"]["LA"]    = "language"     # Language
config["NEWS"]["M1"]    = "pages"        # Start Page
config["NEWS"]["M3"]    = ""             # Type of Article
config["NEWS"]["M4"]    = ""             # Citavi
config["NEWS"]["N1"]    = "note"         # Notes
config["NEWS"]["N2"]    = "abstract"     # like AB
config["NEWS"]["NV"]    = ""             # Frequency
config["NEWS"]["PB"]    = "publisher"    # Publisher
config["NEWS"]["PY"]    = "year"         # Year
config["NEWS"]["RI"]    = ""             # Reviewed Item
config["NEWS"]["RN"]    = ""             # Research Notes
config["NEWS"]["RP"]    = ""             # Reprint Edition
config["NEWS"]["SE"]    = ""             # Section
config["NEWS"]["SN"]    = "issn"         # ISSN
config["NEWS"]["SP"]    = "pages"        # Start Page
config["NEWS"]["ST"]    = "shorttitle"   # Short Title
config["NEWS"]["SV"]    = ""             # ?
config["NEWS"]["T1"]    = "title"        # Title
config["NEWS"]["T2"]    = ""             # Newspaper
config["NEWS"]["T4"]    = "subtitle"     # subtitle
config["NEWS"]["T5"]    = "titleaddon"   # titleaddon
config["NEWS"]["TA"]    = ""             # Translated Author
config["NEWS"]["TI"]    = "title"        # Title
config["NEWS"]["TT"]    = ""             # Translated Title
config["NEWS"]["U6"]    = ""             # like L1
config["NEWS"]["UR"]    = "url"          # URL
config["NEWS"]["VL"]    = "volume"       # Volume
config["NEWS"]["Y2"]    = "date"         # Date of last change
config["NEWS"]["Y3"]    = "urldate"      # Access Date

config["PCOMM"]["A1"]   = "author"       # primary author
config["PCOMM"]["A2"]   = "author"       # secondary author / Recipient
config["PCOMM"]["A3"]   = "author"       # tertiary author
config["PCOMM"]["A4"]   = "author"       # Involved Person
config["PCOMM"]["AB"]   = "abstract"     # Abstract
config["PCOMM"]["AD"]   = ""             # Author Address
config["PCOMM"]["AN"]   = ""             # Accession Number
config["PCOMM"]["AU"]   = "author"       # Author
config["PCOMM"]["C1"]   = ""             # Sender's EMail
config["PCOMM"]["C1"]   = "venue"        # Place Published
config["PCOMM"]["C2"]   = ""             # Recieipients EMail
config["PCOMM"]["C3"]   = ""             # Proceedings Title
config["PCOMM"]["C4"]   = "eventdate"    # Event Date
config["PCOMM"]["C5"]   = ""             # Packaging Method
config["PCOMM"]["C7"]   = "eventtitle"   # Event Title
config["PCOMM"]["CA"]   = ""             # Caption
config["PCOMM"]["CN"]   = ""             # Call Number
config["PCOMM"]["CY"]   = "location"     # City
config["PCOMM"]["DA"]   = "date"         # Date
config["PCOMM"]["DA"]   = ""             # Date
config["PCOMM"]["DB"]   = ""             # Name of Database
config["PCOMM"]["DO"]   = "doi"          # DOI
config["PCOMM"]["DP"]   = ""             # Database Provider
config["PCOMM"]["ED"]   = "editor"       # Editor
config["PCOMM"]["ER"]   = ""             # End of Record
config["PCOMM"]["ET"]   = "edition"      # Edition
config["PCOMM"]["H1"]   = ""             # ?
config["PCOMM"]["H2"]   = ""             # ?
config["PCOMM"]["ID"]   = ""             # Reference ID
config["PCOMM"]["IN"]   = "organization" # Institution
config["PCOMM"]["IS"]   = "issue"        # Reihennummer
config["PCOMM"]["J2"]   = ""             # Abbreviation
config["PCOMM"]["KW"]   = "keywords"     # Keywords
config["PCOMM"]["L1"]   = ""             # File Attachments
config["PCOMM"]["L2"]   = ""             # ?
config["PCOMM"]["L3"]   = ""             # ?
config["PCOMM"]["L4"]   = ""             # Figure
config["PCOMM"]["LA"]   = "language"     # Language
config["PCOMM"]["LB"]   = ""             # Label
config["PCOMM"]["M1"]   = ""             # Folio Number
config["PCOMM"]["M3"]   = "type"         # Type
config["PCOMM"]["M4"]   = ""             # Citavi
config["PCOMM"]["N1"]   = "note"         # Notes
config["PCOMM"]["N2"]   = "abstract"     # like AB
config["PCOMM"]["NV"]   = ""             # Communication Number
config["PCOMM"]["PB"]   = "publisher"    # Publisher
config["PCOMM"]["PY"]   = "year"         # Year
config["PCOMM"]["RN"]   = ""             # Research Notes
config["PCOMM"]["SP"]   = "pagetotal"    # Pages
config["PCOMM"]["ST"]   = "shorttitle"   # Short Title
config["PCOMM"]["SV"]   = ""             # ?
config["PCOMM"]["T1"]   = "title"        # Title
config["PCOMM"]["T2"]   = "series"       # Reihentitel
config["PCOMM"]["T4"]   = "subtitle"     # Subtitle
config["PCOMM"]["TA"]   = ""             # Translated Author
config["PCOMM"]["TI"]   = "title"        # Title
config["PCOMM"]["TS"]   = ""             # Title source
config["PCOMM"]["TT"]   = ""             # Translated Title
config["PCOMM"]["U3"]   = "note"         # Note
config["PCOMM"]["U6"]   = ""             # like L1
config["PCOMM"]["UR"]   = "url"          # URL
config["PCOMM"]["Y2"]   = "date"         # Date of last change
config["PCOMM"]["Y3"]   = "urldate"      # Access Date

config["THES"]["A1"]    = "author"      # primary author
config["THES"]["A2"]    = "author"      # secondary author
config["THES"]["A3"]    = "author"      # tertiary author / Advisor
config["THES"]["A4"]    = ""            # Subsidiary Author / Translator
config["THES"]["AB"]    = "abstract"    # Abstract
config["THES"]["AD"]    = ""            # Author Address
config["THES"]["AN"]    = ""            # Accession Number
config["THES"]["AU"]    = "author"      # Author
config["THES"]["C1"]    = "venue"       # Place Published
config["THES"]["C2"]    = ""            # Year Published
config["THES"]["C3"]    = ""            # Proceedings Title
config["THES"]["C4"]    = "eventdate"   # Event Date
config["THES"]["C5"]    = ""            # Packaging Method
config["THES"]["C7"]    = "eventtitle"  # Event Title
config["THES"]["CA"]    = ""            # Caption
config["THES"]["CN"]    = ""            # Call Number
config["THES"]["CY"]    = "location"    # City
config["THES"]["DA"]    = "date"        # Date
config["THES"]["DB"]    = ""            # Name of Database
config["THES"]["DO"]    = "doi"         # DOI
config["THES"]["DP"]    = ""            # Database Provider
config["THES"]["ER"]    = ""            # End of Record
config["THES"]["ET"]    = "edition"     # Edition
config["THES"]["H1"]    = ""            # ?
config["THES"]["H2"]    = ""            # ?
config["THES"]["ID"]    = ""            # Reference ID
config["THES"]["IS"]    = "issue"       # Reihennummer
config["THES"]["KW"]    = "keywords"    # Keywords
config["THES"]["L1"]    = ""            # File Attachments
config["THES"]["L2"]    = ""            # ?
config["THES"]["L3"]    = ""            # ?
config["THES"]["L4"]    = ""            # Figure
config["THES"]["LA"]    = "language"    # Language
config["THES"]["LB"]    = ""            # Label
config["THES"]["M1"]    = ""            # Document Number
config["THES"]["M3"]    = "type"        # Thesis Type
config["THES"]["M4"]    = ""            # Citavi
config["THES"]["N1"]    = "note"        # Notes
config["THES"]["N2"]    = "abstract"    # like AB
config["THES"]["PB"]    = "institution" # University
config["THES"]["PY"]    = "year"        # Year
config["THES"]["RN"]    = ""            # Research Notes
config["THES"]["SP"]    = "pagetotal"   # Number of Pages
config["THES"]["ST"]    = "shorttitle"  # Short Title
config["THES"]["SV"]    = ""            # ?
config["THES"]["T1"]    = "title"       # Title
config["THES"]["T2"]    = "subtitle"    # Subtitle
config["THES"]["T2"]    = ""            # Academic Department
config["THES"]["T3"]    = "series"      # Reihentitel
config["THES"]["T4"]    = "subtitle"    # subtitle ?
config["THES"]["T5"]    = "titleaddon"  # titleaddon
config["THES"]["TA"]    = ""            # Translated Author
config["THES"]["TI"]    = "title"       # Title
config["THES"]["TS"]    = ""            # Title source
config["THES"]["TT"]    = ""            # Translated Title
config["THES"]["U2"]    = "note"        # Note
config["THES"]["U6"]    = ""            # like L1
config["THES"]["UR"]    = "url"         # URL
config["THES"]["VL"]    = ""            # Degree
config["THES"]["Y2"]    = "date"        # Date of last change
config["THES"]["Y3"]    = "urldate"     # Access Date

config["UNPB"]["A1"]    = "author"       # primary author
config["UNPB"]["A2"]    = "editor"       # Series Editor
config["UNPB"]["A3"]    = "author"       # tertiary author
config["UNPB"]["A4"]    = ""             # Subsidiary Author / Translator
config["UNPB"]["AB"]    = "abstract"     # Abstract
config["UNPB"]["AD"]    = ""             # Author Address
config["UNPB"]["AU"]    = "author"       # Author
config["UNPB"]["C1"]    = "venue"        # Place Published
config["UNPB"]["C2"]    = ""             # Year Published
config["UNPB"]["C3"]    = ""             # Proceedings Title
config["UNPB"]["C4"]    = "eventdate"    # Event Date
config["UNPB"]["C5"]    = ""             # Packaging Method
config["UNPB"]["C7"]    = "eventtitle"   # Event Title
config["UNPB"]["CA"]    = ""             # Caption
config["UNPB"]["CY"]    = "location"     # City
config["UNPB"]["DA"]    = "date"         # Date
config["UNPB"]["DB"]    = ""             # Name of Database
config["UNPB"]["DO"]    = "doi"          # DOI
config["UNPB"]["DP"]    = ""             # Database Provider
config["UNPB"]["ED"]    = "editor"       # Editor
config["UNPB"]["ER"]    = ""             # End of Record
config["UNPB"]["ET"]    = "version"      # Edition
config["UNPB"]["H1"]    = ""             # ?
config["UNPB"]["H2"]    = ""             # ?
config["UNPB"]["ID"]    = ""             # Reference ID
config["UNPB"]["J2"]    = ""             # Abbreviation
config["UNPB"]["KW"]    = "keywords"     # Keywords
config["UNPB"]["L1"]    = ""             # File Attachments
config["UNPB"]["L2"]    = ""             # ?
config["UNPB"]["L3"]    = ""             # ?
config["UNPB"]["L4"]    = ""             # Figure
config["UNPB"]["LA"]    = "language"     # Language
config["UNPB"]["LB"]    = ""             # Label
config["UNPB"]["M1"]    = "number"       # Number
config["UNPB"]["M3"]    = "type"         # Type of Work
config["UNPB"]["M4"]    = ""             # Citavi
config["UNPB"]["N1"]    = "note"         # Notes
config["UNPB"]["N2"]    = "abstract"     # like AB
config["UNPB"]["PB"]    = "organization" # Institution
config["UNPB"]["PY"]    = "year"         # Year
config["UNPB"]["RN"]    = ""             # Research Notes
config["UNPB"]["SN"]    = ""             # Reihennummer
config["UNPB"]["SN"]    = "isbn"         # IDBN/ISSN
config["UNPB"]["SP"]    = "pagetotal"    # Pages
config["UNPB"]["ST"]    = "shorttitle"   # Short Title
config["UNPB"]["SV"]    = ""             # ?
config["UNPB"]["T1"]    = "title"        # Title
config["UNPB"]["T2"]    = "series"       # Series Title
config["UNPB"]["T3"]    = ""             # Department
config["UNPB"]["T4"]    = "subtitle"     # subtitle
config["UNPB"]["T5"]    = "titleaddon"   # titleaddon
config["UNPB"]["TA"]    = ""             # Translated Author
config["UNPB"]["TI"]    = "title"        # Title of Work
config["UNPB"]["TT"]    = ""             # Translated Title
config["UNPB"]["U3"]    = "note"         # Note
config["UNPB"]["U6"]    = ""             # like L1
config["UNPB"]["UR"]    = "url"          # URL
config["UNPB"]["Y1"]    = "year"         # Year
config["UNPB"]["Y2"]    = "date"         # Date of last change
config["UNPB"]["Y3"]    = "urldate"      # Access Date

# -------------------------------------------------------------
# Some declarations and initializations

oneline       = ""                            # content of a source line
linenr        = 0                             # line number in source file
onerecord     = {}                            # the content of a record
allrecordkeys = []                            # container for all record keys
ristype       = ""                            # actual RIS type
status        = "out of record"               # status: in record / in note / in abstract / out of record
fieldwidth    = 13                            # width of the BibTeX keys
newline       = "\n" + (fieldwidth + 2) * " " #
verbose       = False                         # Flag: verbose output
bibtexkeys    = False                         # Flag: show the generated BibTeX keys
actDate       = time.strftime("%Y-%m-%d")     # actual date of program execution
actTime       = time.strftime("%X")           # actual time of program execution
call          = sys.argv                      # parameter of the program call

arguments = " "
for f in range(1,len(call)):
    arguments = arguments + call[f] + " "

# -------------------------------------------------------------
# Defaults

out_file        = ""                                 # actual name for output file
out_default     = "out-test.bib"                     # default name for output file
in_file         = ""                                 # actual name for input file
in_default      = ""                                 # default name for input file
correction_file = ""                                 # actual name for correction file
correction_default = ""                              # default name for correction file
skip_default    = "[]"                               # default for -s 

# -------------------------------------------------------------
# Texts for argparse

in_text         = "name for input file"              # 
out_text        = "name for output file"             #
correction_text = "name for a file with additional conversion rules"    
verbose_text    = "Flag: verbose output"             #
bibtex_text     = "Flag: show the generated BibTeX keys" #
author_text     = "author of the program"            #
version_text    = "version of the program"           #
program_text    = "converts RIS files to .bib files" #
skip_text       = "skip BibTeX fields"               # 

# -------------------------------------------------------------
# Regular expressions

p1 = re.compile("^[A-Z][A-Z0-9]$")                   # regular expression: RIS keys
p2 = re.compile("^[A-Z]+")                           # regular expression: RIS types
p3 = re.compile("^@[a-z]+")                          # regular expression: BibTeX types
p4 = re.compile("  -")                               # separator between RIS key and content
p5 = re.compile("[;,]")                              # 

# -------------------------------------------------------------
# Some functions

def recordkey(o):
    global allrecordkeys
    
    if ("author" in o) and o["author"] != "":       # author name
        tmp1 = o["author"]
    elif ("editor" in o) and o["editor"] != "":
        tmp1 = o["editor"]
    elif ("organization" in o) and o["organization"] != "":
        tmp1 = o["organization"]
    else:
        tmp1 = "N. N."
    tmp1  = re.sub("[' ]", "", tmp1)                # delete some characters
    tmp1a = unidecode(p5.split(tmp1)[0])            # mapping to ASCII
        
    if ("year" in o) and o["year"] != "":           # year
        tmp2  = o["year"]
        tmp2a = p5.split(tmp2)[0]
    else:
        tmp2a = ""
    tmp2a = re.sub("[' ]", "", tmp2a)               # delete some characters

    nr     = 0                                 
    tmpkey = (tmp1a, tmp2a, chr(97 + nr))
    while tmpkey in allrecordkeys:                  # loop over potential keys
        nr     = nr + 1
        tmpkey = (tmp1a, tmp2a, chr(97 + nr))
    allrecordkeys.append(tmpkey)                    # container for all record keys
    return tmp1a + "." + tmp2a + chr(97 + nr)


# =============================================================
# The Process

# -------------------------------------------------------------
# Parsing the arguments

parser = argparse.ArgumentParser(description = program_text + " [" + programname + "; " +
                                 "Version: " + programversion + " (" + programdate + ")]")
parser._positionals.title = 'Positional parameters'
parser._optionals.title   = 'Optional parameters'

parser.add_argument(help    = in_text + "; Default: " + "%(default)s",
                    dest    = "in_file",
                    default = in_default)

parser.add_argument("-a", "--author",
                    help    = author_text,
                    action  = 'version',
                    version = programauthor + " (" + authoremail + ", " +
                    authorinstitution + ")")

parser.add_argument("-o", "--output",
                    help    = out_text + "; Default: " + "%(default)s",
                    dest    = "out_file",
                    default = out_default)

parser.add_argument("-c", "--correction",
                    help    = correction_text + "; Default: " + "%(default)s",
                    dest    = "correction_file",
                    default = correction_default)

parser.add_argument("-s", "--skip",
                    help    = skip_text + "; Default: " + "%(default)s",
                    dest    = "skip",
                    default = skip_default)

parser.add_argument("-v", "--verbose",
                    help = verbose_text + "; Default: " + "%(default)s",
                    action = "store_true",
                    default = verbose)

parser.add_argument("-b", "--bibtexkeys",
                    help = bibtex_text + "; Default: " + "%(default)s",
                    action = "store_true",
                    default = bibtexkeys)

parser.add_argument("-V", "--version",
                    help    = version_text,
                    action  = 'version',
                    version = '%(prog)s ' + programversion + " (" + programdate + ")")

args            = parser.parse_args()   # get all arguments
out_file        = args.out_file         # name of the output file
in_file         = args.in_file          # name of the input file
correction_file = args.correction_file  # name of the file with the additional conversion rules
verbose         = args.verbose          # Flag: verbose output
bibtexkeys      = args.bibtexkeys       # Flag: output the generated BibTeX keys
skip            = args.skip             # BibTeX keys to be skipped

# -------------------------------------------------------------
# Open the files

try:                                                         # open input file
    inp  = open(in_file, encoding="utf-8-sig", mode="r")
except FileNotFoundError:
    if verbose:
        print("--- input file", in_file,  "could not be opened; program terminated")
    sys.exit("--- program is terminated")

out  = open(out_file, encoding="utf-8", mode="w")            # open output file

if correction_file != "":                                    # open correction file
    try:
        ini = open(correction_file, encoding="utf-8-sig", mode="r")
        for ff in ini:
            exec(ff)
        ini.close()
        if verbose:
            print("--- File", correction_file, "with additional conversion rules read")
    except IOError:
        if verbose:
            print("--- Correction file", correction_file,  "could not be opened")

# -------------------------------------------------------------
# Loop

# linenr   : number of line
# line     : a input line
# oneline  : a input line (stripped)
# lparts   : online splitted on p4
# status   : in record / in note / in abstract / out of record
# ristype  : actual RIS type
# bibtype  : actual BibTeX type
# riskey   : actual RIS key
# bibfield : actual BibTeX field
# onerecord: the actual content of a BibTeX record
# config   : conversion table
# verbose  : Flag: verbose output
# skip     : BibTeX items to be skipped

out.write("% " + out_file + " \n")
out.write("% generated by " + programname + " (version: "  + programversion +
          " of " + programdate + ")\n")
out.write("% Date          : " + actDate + "; Time: " + actTime + "\n")
out.write("% Input file    : " + in_file + "\n")
if skip != "":
    out.write("% skipped fields: " + skip + "\n")
out.write("% Program Call  : " + programname + arguments + "\n\n")

if verbose:
    print("- Program call:", programname + arguments)

for line in inp:                                             # loop over all input lines
    linenr  = linenr + 1                                     # counter
    oneline = line.strip()                                   # strip line
    lparts  = p4.split(oneline)                              # split line
    if p1.match(lparts[0]):                                  # (1) 1st part of line match p1
        riskey = lparts[0]                                   #     get riskey
        
        if riskey == "TY":                                   # (2) process TY
            if status != "out of record":                    #     previous record is not completed
                if verbose: print("--- Line", str(linenr) +
                                  ": actual record not completed by 'ER  -'; skipped")
            status    = "in record"                          #     status set to "in record"
            onerecord = {}                                   #     container onerecord initialized
            ristype   = lparts[1][1:]                        #     get RIS type
            if p2.match(ristype) and (ristype in config):    #     known ristype 
                bibtype = config[ristype]["TY"]              #     get bibtype
            else:                                            #     unknown ristype
                if verbose:
                    print("--- Line", str(linenr) + ": RIS type incorrect in", oneline,
                          "; 'GEN' supposed")
                ristype = "GEN"                              #     ristype set to "GEN"
                bibtype = config[ristype]["TY"]              #     get bibtype
        elif riskey == "N1":                                 # (2) process N1
            status   = "in note"                             #     status set to "in note"
            bibfield = config[ristype][riskey]               #     get bibfield
            if bibfield in onerecord:
                onerecord[bibfield] = onerecord[bibfield] + newline + lparts[1][1:] 
            else:
                onerecord[bibfield] = lparts[1][1:]
        elif riskey == "AB":                                 # (2) process AB 
            status = "in abstract"                           #     status set to "in abstract"
            bibfield = config[ristype][riskey]               #     get bibfield
            if bibfield in onerecord:
                onerecord[bibfield] = onerecord[bibfield] + newline + lparts[1][1:]
            else:
                onerecord[bibfield] = lparts[1][1:]
        elif riskey == "ER":                                 # (2) process ER
            tmp0 = recordkey(onerecord)                      #     get recordkey
            out.write(bibtype + "{" + tmp0 + ",\n")          #     first line of a BibTeX record
            for f in onerecord:                              #     process all in onerecord collected lines
                if f not in skip:
                    if f == "author":                        #     author: "; " ---> " and "
                        onerecord[f] = re.sub("; ", " and ", onerecord[f])
                    if f == "pages":                         #     pages: "; " ---> "--"
                        onerecord[f] = re.sub("; ", "--", onerecord[f])
                    out.write(f.ljust(fieldwidth) + "= {" + onerecord[f]+'},\n')
            out.write("}\n")                                 #     last line of a BibTeX record
            onerecord = {}                                   #     initialize onerecord
            status    = "out of record"                      #     status set
        elif not (riskey in ["TY", "N1", "AB", "ER"]):       # (2) not TY, N1, AB, ER 
            status = "in record"                             #     status set
            if (riskey in config[ristype]):                  # (3) riskey known in the actual record
                bibfield = config[ristype][riskey]           #     get bibfield
                if bibfield == "":                           # (4)
                    if verbose:
                        print("--- Line", str(linenr) + ": empty bibfield for " ,
                              ristype, riskey, "in '" + oneline + "'", "; collected in 'note'")
                    if lparts[1][1:] != "":
                        if 'note' in onerecord:
                            onerecord['note'] = onerecord['note'] + newline + oneline
                        else:
                            onerecord['note'] = oneline
                else:                                        # (4)
                    if bibfield in onerecord:
                        onerecord[bibfield] = onerecord[bibfield] + "; " + lparts[1][1:]
                    else:
                         onerecord[bibfield] = lparts[1][1:]
            else:                                            # (3) riskey unknown in the actual record
                if verbose:
                    print("--- Line", str(linenr) + ": unknown riskey for", ristype,
                          riskey, "in '" + oneline + "'")
                if lparts[1][1:] != "":
                    if 'note' in onerecord:
                        onerecord['note'] = onerecord['note'] + newline + oneline
                    else:
                        onerecord['note'] = oneline 
    elif status == "out of record":                          # (1) "out of record"
        out.write(oneline + "\n")
    elif status == "in abstract":                            # (1) "in abstract"
        if bibfield in onerecord:
            onerecord["abstract"] = onerecord["abstract"] + " " + oneline
        else:
            onerecord["abstract"] = oneline
    elif status == "in note":                                # (1) "in note"
        if bibfield in onerecord:
            onerecord["note"] = onerecord["note"] + newline + oneline
        else:
            onerecord["note"] = oneline
    

# =============================================================
# The End

# -------------------------------------------------------------
# Close the files

inp.close()
out.close()
if verbose:
    print("- Program finished")

# -------------------------------------------------------------
# Process option -b 

if bibtexkeys:
    print("\n- Generated BibTeX keys:")
    for f in allrecordkeys: print(f[0] + "." + f[1] + str(f[2]))

