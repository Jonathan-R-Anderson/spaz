from flask import render_template, jsonify, request
from ..routes import blueprint
import logging, json
from ...utils.contracts import (
    gremlinProfileAddress, gremlinProfileABI,
    gremlinLeaderboardAddress, gremlinLeaderboardABI,
    gremlinJournalAddress, gremlinJournalABI
)
from ...services.stream import RTMP_URLS

@blueprint.route('/')
def index():
    logging.debug("Rendering welcome page.")
    return render_template('welcome.html')

@blueprint.route('/dashboard/<eth_address>', methods=['GET'])
def home(eth_address):
    logging.debug(f"Rendering dashboard for {eth_address}")
    return render_template('dashboard.html', eth_address=eth_address,
                           gremlinProfileABI=json.dumps(gremlinProfileABI, ensure_ascii=False),
                           gremlinProfileAddress=gremlinProfileAddress,
                           gremlinLeaderboardAddress=gremlinLeaderboardAddress,
                           gremlinLeaderboardABI=json.dumps(gremlinLeaderboardABI, ensure_ascii=False),
                           gremlinJournalAddress=gremlinJournalAddress,
                           gremlinJournalABI=json.dumps(gremlinJournalABI, ensure_ascii=False))

@blueprint.route('/users/<eth_address>', methods=['POST', 'GET'])
def user_profile(eth_address):
    if request.method == 'POST':
        current_user_eth_address = request.json.get('current_user_eth_address')
        is_owner = current_user_eth_address.lower() == eth_address.lower()
        rtmp_url = RTMP_URLS.get(eth_address, "psichos.is") if is_owner else "psichos.is"
        logging.debug(f"Profile POST for {eth_address}, owner={is_owner}")
        return jsonify({"is_owner": is_owner, "rtmp_stream_url": rtmp_url})
    logging.debug(f"Rendering profile for {eth_address}")
    return render_template('profile.html', eth_address=eth_address,
                           gremlinProfileABI=json.dumps(gremlinProfileABI, ensure_ascii=False),
                           gremlinProfileAddress=gremlinProfileAddress,
                           gremlinLeaderboardAddress=gremlinLeaderboardAddress,
                           gremlinLeaderboardABI=json.dumps(gremlinLeaderboardABI, ensure_ascii=False),
                           gremlinJournalAddress=gremlinJournalAddress,
                           gremlinJournalABI=json.dumps(gremlinJournalABI, ensure_ascii=False))