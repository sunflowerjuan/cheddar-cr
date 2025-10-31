from flask import Flask
from routes.cr_router import router_bp

app = Flask(__name__)

app.register_blueprint(router_bp)

@app.route('/')
def home():
    return "Data Collector is running."

if __name__ == "__main__":
    app.run(debug=True)
