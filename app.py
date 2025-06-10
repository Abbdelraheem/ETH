from flask import Flask, render_template, jsonify, request
from threading import Thread, Event
import logging
from utils import load_wallet
from scanner import scan_blocks

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# حالة النظام
system_status = {
    'running': False,
    'wallet_connected': False,
    'last_scan_block': 0,
    'activity_log': [],
    'stats': {
        'total_rewards': 0.0,
        'total_tokens': 0,
        'successful_claims': 0,
        'failed_claims': 0,
        'contracts_scanned': 0
    }
}

# حدث لإيقاف المسح
stop_event = Event()

@app.route('/')
def index():
    wallet_address, _ = load_wallet()
    return render_template('index.html', wallet_address=wallet_address)

@app.route('/api/start', methods=['POST'])
def start_scan():
    if not system_status['running']:
        system_status['running'] = True
        stop_event.clear()
        Thread(target=run_scanner).start()
        log_activity("بدأ المسح النشط للعقود")
        return jsonify({'status': 'started'})
    return jsonify({'status': 'already_running'})

@app.route('/api/stop', methods=['POST'])
def stop_scan():
    if system_status['running']:
        system_status['running'] = False
        stop_event.set()
        log_activity("تم إيقاف المسح")
        return jsonify({'status': 'stopped'})
    return jsonify({'status': 'not_running'})

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'running': system_status['running'],
        'stats': system_status['stats'],
        'log': system_status['activity_log'][-20:]  # آخر 20 إدخال
    })

def run_scanner():
    try:
        scan_blocks(stop_event, system_status)
    except Exception as e:
        log_activity(f"خطأ في المسح: {str(e)}", "error")
        system_status['running'] = False

def log_activity(message, level="info"):
    entry = {
        'time': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
        'message': message,
        'level': level
    }
    system_status['activity_log'].append(entry)
    app.logger.info(f"[{level.upper()}] {message}")

if __name__ == '__main__':
    _, private_key = load_wallet()
    if private_key:
        system_status['wallet_connected'] = True
        log_activity("تم تحميل المحفظة بنجاح", "success")
    app.run(host='0.0.0.0', port=5000, debug=True)