from flask import render_template

from app import create_app

#Creates and load the application to be run
app = create_app()

#Run the application
if __name__ == '__main__':
    app.run(debug=True, port=8080)
