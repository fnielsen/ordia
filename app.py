"""Script to start webserving."""


from ordia.app import create_app


DEBUG = True

app = create_app()


if __name__ == '__main__':
    app.run(debug=DEBUG)
