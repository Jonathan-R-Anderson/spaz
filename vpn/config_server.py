from flask import Flask, request, render_template_string
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TEMPLATE = '''
<h2>OpenVPN Initial Setup</h2>
<form method="POST">
  Client Name: <input name="client"><br><br>
  <input type="submit" value="Generate OVPN">
</form>
'''

@app.route("/", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        client = request.form["client"]
        os.system(f"easyrsa build-client-full {client} nopass")
        os.system(f"ovpn_getclient {client} > /etc/openvpn/{client}.ovpn")
        return f"<h3>Config created for {client}</h3><a href='/{client}.ovpn'>Download</a>"
    return render_template_string(TEMPLATE)

@app.route("/<client>.ovpn")
def download(client):
    return open(f"/etc/openvpn/{client}.ovpn").read(), 200, {
        "Content-Type": "application/x-openvpn-profile",
        "Content-Disposition": f"attachment; filename={client}.ovpn"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
