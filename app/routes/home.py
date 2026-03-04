from flask import Blueprint,render_template
homePage = Blueprint('home', __name__)

@homePage.route("/")
def home():
    return render_template("home.html")