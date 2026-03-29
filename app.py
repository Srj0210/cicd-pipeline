from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "service": "DevOps Demo API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development")
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/api/info")
def info():
    return jsonify({
        "app": "cicd-pipeline-demo",
        "author": "Suraj Maitra",
        "description": "A containerized Flask API with full CI/CD pipeline using GitHub Actions",
        "tech_stack": ["Python", "Flask", "Docker", "GitHub Actions", "Trivy", "Hadolint"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
