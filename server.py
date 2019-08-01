import dash

# external css
font = 'https://fonts.googleapis.com/icon?family=Material+Icons'
external_stylesheets = [font]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets
)

# adding custom meta tags
app = dash.Dash(meta_tags=[
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
server = app.server
