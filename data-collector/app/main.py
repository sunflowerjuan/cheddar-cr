from flask import Flask
from flasgger import Swagger
from routes.cr_router import router_bp
from utils.config import swagger_config,template

app = Flask(__name__)
swagger = Swagger(app, config=swagger_config, template=template)
app.register_blueprint(router_bp)

@app.route('/')
def home():
    return "Data Collector is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
