Architecture:

Main: app.py - runs the app and gets the layout. index url

secondary 1: company.py - makes the layout (mostly graphs and tables) for the company pages. Url is {ticker}.co


Backend:
    components.py - creates the html for the components.
    usedata.py - reads the data files (csv) so the data is usable.
    dataDownloads.py - downloads all the data.


Need to:
sector.py
stocks.py
