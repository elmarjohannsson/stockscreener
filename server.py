import dash
# from settings import PATH

# # external css
# icons = 'https://fonts.googleapis.com/icon?family=Material+Icons'
# external_stylesheets = [icons, {"href": icons, "rel": "stylesheet"}]


# external_scripts = [
#     {"src": "https://code.jquery.com/jquery-3.4.1.min.js",
#      "integrity": "sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo=",
#      "crossorigin": "anonymous"}
# ]

# assets_url_path=f"{PATH}/assets"

app = dash.Dash(__name__, meta_tags=[
    # A description of the app, used by e.g.
    # search engines when displaying search results.
    {
        'name': 'description',
        'content': 'Stock screener'
    },
    # A tag that tells Internet Explorer (IE)
    # to use the latest renderer version available
    # to that browser (e.g. Edge)
    {
        'http-equiv': 'X-UA-Compatible',
        'content': 'IE=edge'
    },
    # A tag that tells the browser not to scale
    # desktop widths to fit mobile screens.
    # Sets the width of the viewport (browser)
    # to the width of the device, and the zoom level
    # (initial scale) to 1.
    #
    # Necessary for "true" mobile support.
    {
        'name': 'viewport',
        'content': 'width=device-width, initial-scale=1.0'
    }
])

app.config['suppress_callback_exceptions'] = True
app.title = "Stockscreener.dk - Free Financial Data For The Nordic Markets!"
