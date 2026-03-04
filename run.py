from flask import render_template

from app import create_app

app = create_app()

@app.route("/")
def home():
    return render_template("home.html")    

@app.route("/create-admin")
def create_admin():
    return render_template("admin_account.html")

if __name__ == '__main__':
    app.run(debug=True)
