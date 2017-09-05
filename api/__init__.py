from nails import init_app

app = None
app = init_app(__file__, '/api/v1/')

@app.route('/api/')
def app_api():
    return 'Hello, Nails.py!'

@app.route('/api/v1/')
def app_v1():
    return 'Hello, Nails.py v1!'
