import dash

app = dash.Dash(__name__)
server = app.server
app.config.supress_callback_exceptions = True

spectre_css = 'https://unpkg.com/spectre.css/dist/spectre.min.css'

external_css = [spectre_css]
# adding all external css
for css in external_css:
    app.css.append_css({"external_url": css})

# adding all external scripts
# external_js = []
# for js in external_js:
#     app.scrips.append_script({'external_js': js})
