from flask import Flask, request, render_template, send_file
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, template_folder="templates")

@app.route("/", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        client = request.form["client"]
        os.system(f"easyrsa build-client-full {client} nopass")
        os.system(f"ovpn_getclient {client} > /etc/openvpn/{client}.ovpn")
        return f"<h3>Config created for {client}</h3><a href='/{client}.ovpn'>Download</a>"
    return render_template("index.html")

@app.route("/<client>.ovpn")
def download(client):
    return send_file(
        f"/etc/openvpn/{client}.ovpn",
        mimetype="application/x-openvpn-profile",
        as_attachment=True,
        download_name=f"{client}.ovpn"
    )

@app.route("/shutdown", methods=["POST"])
def shutdown():
    os.system("kill 1") 
    return "Shutting down...", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6660)
