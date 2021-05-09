
from flask import Blueprint, render_template, redirect, jsonify, request, send_file
from flask import current_app as app
from user_management import check_logged_in
from bitcoin_info import *
from lightning_info import *
from electrum_info import *
from device_info import *
from thread_functions import *
from systemctl_info import *
from application_info import *
from messages import *
import cStringIO
import json
import subprocess
import re
import os

mynode_api = Blueprint('mynode_api',__name__)


### Page functions
@mynode_api.route("/api/get_bitcoin_info")
def api_get_bitcoin_info():
    check_logged_in()

    data = {}
    data["current_block"] = get_mynode_block_height()
    data["block_height"] = get_bitcoin_block_height()
    data["peer_count"] = get_bitcoin_peer_count()
    #data["difficulty"] = get_bitcoin_difficulty() # Dont send difficulty, it causes errors in jsonify
    data["mempool_size"] = get_bitcoin_mempool_size()

    # Add blocks
    data["recent_blocks"] = None
    blocks = get_bitcoin_recent_blocks()
    if blocks != None:
        for b in blocks:
            # Remove TX list for faster processing
            b["tx"] = None
            # Remove difficulty since JSON can't parse large floats (???)
            b["difficulty"] = None
        data["recent_blocks"] = blocks

    #app.logger.info("api_get_bitcoin_info data: "+json.dumps(data))
    return jsonify(data)

@mynode_api.route("/api/get_lightning_info")
def api_get_lightning_info():
    check_logged_in()

    data = {}
    data["peer_count"] = get_lightning_peer_count()
    data["channel_count"] = get_lightning_channel_count()
    data["lnd_ready"] = is_lnd_ready()
    data["balances"] = get_lightning_balance_info()
    data["channels"] = get_lightning_channels()

    return jsonify(data)

@mynode_api.route("/api/get_service_status")
def api_get_service_status():
    check_logged_in()

    data = {}
    data["status"] = "gray"
    data["color"] = ""
    data["sso_token"] = ""

    service = request.args.get('service')

    # Try standard status API
    data["status"] = get_application_status(service)
    data["color"] = get_application_status_color(service)
    data["sso_token"] = get_application_sso_token(service)
    return jsonify(data)

@mynode_api.route("/api/get_device_info")
def api_get_device_info():
    check_logged_in()

    data = {}
    data["disk_usage"] = get_drive_usage()
    data["cpu"] = get_cpu_usage()
    data["ram"] = get_ram_usage()
    data["temp"] = get_device_temp()
    data["is_installing_docker_images"] = is_installing_docker_images()
    data["is_electrs_active"] = is_electrs_active()

    return jsonify(data)

@mynode_api.route("/api/homepage_needs_refresh")
def api_homepage_needs_refresh():
    check_logged_in()

    data = {}
    data["needs_refresh"] = "no"

    if get_mynode_status() != STATE_STABLE:
        data["needs_refresh"] = "yes"
    if not has_product_key() and not skipped_product_key():
        data["needs_refresh"] = "yes"
    if not get_has_updated_btc_info():
        data["needs_refresh"] = "yes"
    if not is_bitcoin_synced():
        data["needs_refresh"] = "yes"

    return jsonify(data)

@mynode_api.route("/api/get_log")
def api_get_log():
    check_logged_in()

    data = {}
    data["log"] = "LOG MISSING"

    if not request.args.get("app"):
        data["log"] = "NO APP SPECIFIED"
        return jsonify(data)

    app_name = request.args.get("app")
    data["log"] = get_application_log(app_name)
    
    return jsonify(data)

@mynode_api.route("/api/get_qr_code_image")
def api_get_qr_code_image():
    check_logged_in()
    
    img_buf = cStringIO.StringIO()
    url = "ERROR"
    if request.args.get("url"):
        url = request.args.get("url")
    img = generate_qr_code(url)
    img.save(img_buf)
    img_buf.seek(0)
    return send_file(img_buf, mimetype='image/png')

@mynode_api.route("/api/get_message")
def api_get_message():
    check_logged_in()
    
    funny = False
    if request.args.get("funny"):
        funny = True
    
    data = {}
    data["message"] = get_message(funny)
    return jsonify(data)

@mynode_api.route("/api/toggle_setting")
def api_toggle_setting():
    check_logged_in()

    data = {}
    data["status"] = "unknown"

    if not request.args.get("setting"):
        data["status"] = "no_setting_specified"
        return jsonify(data)

    setting = request.args.get("setting")
    if setting == "pinned_lightning_details":
        toggle_pinned_lightning_details()
        data["status"] = "success"
    else:
        data["status"] = "unknown_setting"
    
    return jsonify(data)