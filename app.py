"""Script to start webserving."""


from ordia.app import create_app


DEBUG = True


max_ids = None
if DEBUG:
    max_ids = 100

app = create_app(max_ids=max_ids)


if __name__ == '__main__':
    app.run(debug=DEBUG)
