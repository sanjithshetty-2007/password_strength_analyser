# from flask import Flask, render_template, request, jsonify
# import re, math, secrets, string

# app = Flask(__name__)

# def password_rules(password):
#     return {
#         "length": len(password) >= 8,
#         "uppercase": bool(re.search(r"[A-Z]", password)),
#         "lowercase": bool(re.search(r"[a-z]", password)),
#         "number": bool(re.search(r"\d", password)),
#         "special": bool(re.search(r"[^A-Za-z0-9]", password)),
#     }

# def estimate_crack_time(password):
#     charset = 0
#     if re.search(r"[a-z]", password): charset += 26
#     if re.search(r"[A-Z]", password): charset += 26
#     if re.search(r"\d", password): charset += 10
#     if re.search(r"[^A-Za-z0-9]", password): charset += 32

#     if charset == 0:
#         return "Instant 💀"

#     entropy = len(password) * math.log2(charset)
#     guesses_per_sec = 1e9
#     seconds = (2 ** entropy) / guesses_per_sec

#     if seconds < 60: return "Seconds 😬"
#     if seconds < 3600: return "Minutes 😑"
#     if seconds < 86400: return "Hours 👀"
#     if seconds < 31536000: return "Days 😎"
#     if seconds < 315360000: return "Years 😈"
#     return "Centuries 🧠"

# def generate_password(length=16):
#     chars = string.ascii_letters + string.digits + "!@#$%^&*()_+"
#     return "".join(secrets.choice(chars) for _ in range(length))

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/check", methods=["POST"])
# def check():
#     password = request.json.get("password", "")
#     rules = password_rules(password)
#     crack_time = estimate_crack_time(password)
#     return jsonify({"rules": rules, "crack_time": crack_time})

# @app.route("/generate")
# def generate():
#     return jsonify({"password": generate_password()})

# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import re
import math
import secrets
import string
from functools import reduce

app = Flask(__name__)

# ---------------- PASSWORD ANALYZER CLASS ----------------
class PasswordAnalyzer:
    def __init__(self, password: str):
        self.password = password
        self.rules = {
            "length": lambda p: len(p) >= 8,
            "uppercase": lambda p: bool(re.search(r"[A-Z]", p)),
            "lowercase": lambda p: bool(re.search(r"[a-z]", p)),
            "number": lambda p: bool(re.search(r"\d", p)),
            "special": lambda p: bool(re.search(r"[^A-Za-z0-9]", p)),
        }

    def check_rules(self) -> dict:
        """
        Applies all rule lambdas to the password
        Returns a dictionary of rule results
        """
        return {rule: check(self.password) for rule, check in self.rules.items()}

    def calculate_entropy(self) -> float:
        """
        Calculates entropy using character set size
        """
        charset_sizes = [
            26 if re.search(r"[a-z]", self.password) else 0,
            26 if re.search(r"[A-Z]", self.password) else 0,
            10 if re.search(r"\d", self.password) else 0,
            32 if re.search(r"[^A-Za-z0-9]", self.password) else 0,
        ]

        charset = reduce(lambda a, b: a + b, charset_sizes)

        if charset == 0:
            return 0

        return len(self.password) * math.log2(charset)

    def estimate_crack_time(self) -> str:
        """
        Estimates crack time based on entropy
        """
        entropy = self.calculate_entropy()
        guesses_per_second = 1e9

        if entropy == 0:
            return "Instant 💀"

        seconds = (2 ** entropy) / guesses_per_second

        time_scale = [
            (60, "Seconds 😬"),
            (3600, "Minutes 😑"),
            (86400, "Hours 👀"),
            (31536000, "Days 😎"),
            (315360000, "Years 😈"),
        ]

        for limit, label in time_scale:
            if seconds < limit:
                return label

        return "Centuries 🧠"


# ---------------- PASSWORD GENERATOR CLASS ----------------
class PasswordGenerator:
    def __init__(self, length: int = 16):
        self.length = length
        self.characters = (
            string.ascii_lowercase +
            string.ascii_uppercase +
            string.digits +
            "!@#$%^&*()_+"
        )

    def generate(self) -> str:
        """
        Generates cryptographically secure password
        """
        return "".join(secrets.choice(self.characters) for _ in range(self.length))


# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def check():
    password = request.json.get("password", "")
    analyzer = PasswordAnalyzer(password)

    return jsonify({
        "rules": analyzer.check_rules(),
        "crack_time": analyzer.estimate_crack_time()
    })


@app.route("/generate")
def generate():
    generator = PasswordGenerator()
    return jsonify({"password": generator.generate()})


if __name__ == "__main__":
    app.run(debug=True)
