# -*- coding: utf-8 -*-


from flask import Flask, request, url_for, redirect, abort
from tools import Adsl
import time, logging, os

app = Flask(__name__)

adsl_config = {
    'host': '127.0.0.1',
    'port': 6379,
}

LOG_PATH = '/ROOT/logs/web'
FILE_NAME = 'web-' + time.strftime('%Y-%m-%d', time.localtime()) + '.log'
LOG_FILE = LOG_PATH + '/' + FILE_NAME

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s',
                    filemode='a',
                    filename=LOG_FILE)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    return redirect(url_for('adsllist'))


@app.route('/adsl/list')
def adsllist():
    adsl = Adsl(adsl_config['host'], adsl_config['port'])
    parameters = request.args

    if len(parameters) > 0:
        if 'num' in parameters:
            num = int(parameters['num'])

            lines = adsl.getlines()
            i = 0
            ret = ''
            for line in lines:
                if adsl.getstatusbyline(line) == 'available':
                    i += 1
                    str = line + ' ' + adsl.getidcbyline(line) + ':8200 ONLINE'
                    ret += str + '\n'

                    adsl.setstatusbyline(line, status='using')

                    if i >= num:
                        break

            return ret

        elif 'show' in parameters:
            ret = ''
            if parameters['show'].lower() == 'all':
                lines = adsl.getlines()
                for line in lines:
                    str = line + ' ' + adsl.getidcbyline(line) + ':8200 ' + adsl.getadslbyline(line) + ' ' + adsl.getstatusbyline(line)
                    ret += str + '\n'

            return ret
    else:
        ret = ''
        lines = adsl.getlines()
        for line in lines:
            if adsl.getstatusbyline(line) == 'available':
                str = line + ' ' + adsl.getidcbyline(line) +  ':8200 ONLINE'
                ret += str + '\n'

        return ret


@app.route('/adsl/host/report',methods=['POST'])
def adslop():
    adsl = Adsl(adsl_config['host'], adsl_config['port'])

    if 'ip' in request.form:
        if request.headers.get('User-Agent').lower() == 'dj-adsl-backend':
            ips = request.form['ip']
            alllines = adsl.getlines()
            ret = ''
            for ip in ips.split(','):
                for line in alllines:
                    if ip == adsl.getidcbyline(line):
                        adsl.setstatusbyline(line,'dailing')
                        ret += ip + ': ok\n'
                        break
            return ret
        else:
            abort(403)

    elif 'status' in request.form:
        status = request.form['status']
        if status == 'used':
            lines = request.form['lines']

            ret = ''
            for line in lines.split(','):
                if adsl.exists(line):
                    adsl.setstatusbyline(line, 'dailing')
                    ret += line + ': ok\n'
                else:
                    ret += line + ': no this line\n'
            return ret

        elif status == 'new' or status == 'dailed':
            line = request.form['line']
            ip_adsl = request.form['ip_adsl']
            ip_idc = request.form['ip_idc']

            adsl.additem(line, ip_idc, ip_adsl)

            str = line + ':' + ip_idc + ':' + ip_adsl

            return 'Add ' + str + ' successfully!'


if __name__ == '__main__':
    app.run(debug=False, port=8000, host='10.10.65.165')
