# -*- coding: utf-8 -*-


from flask import Flask, request, url_for, redirect
from tools import Adsl

app = Flask(__name__)

adsl_config = {
    'host': '127.0.0.1',
    'port': 6379,
}


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
                    str = line + ' ' + adsl.getidcbyline(line) + ' ' + adsl.getadslbyline(line) + ' ' + adsl.getstatusbyline(line)
                    ret += str + '\n'

                    if i > num:
                        break

            return ret

        elif 'show' in parameters:
            ret = ''
            if parameters['show'].lower() == 'all':
                lines = adsl.getlines()
                for line in lines:
                    str = line + ' ' + adsl.getidcbyline(line) + ' ' + adsl.getadslbyline(line) + ' ' + adsl.getstatusbyline(line)
                    ret += str + '\n'

            return ret

    else:
        ret = ''
        lines = adsl.getlines()
        for line in lines:
            if adsl.getstatusbyline(line) == 'available':
                str = line + ' ' + adsl.getidcbyline(line) + ' ' + adsl.getadslbyline(line) + ' ' + adsl.getstatusbyline(line)
                ret += str + '\n'

        return ret


@app.route('/adsl')
def adslop():
    adsl = Adsl(adsl_config['host'], adsl_config['port'])
    lines = request.args['lines']
    status = request.args['status']

    if status == 'used':
        ret = ''
        for line in lines.split(','):
            if adsl.exists(lines):
                adsl.setstatusbyline(line, 'dailing')
                ret += line + ': ok\n'
            else:
                ret += line + ': no this line\n'

        return ret

    elif status == 'dailed':
        ret = ''
        for line in lines.split(','):
            if adsl.exists(lines):
                adsl.setstatusbyline(line, 'available')
                ret += line + ': ok\n'
            else:
                ret += line + ': no this line\n'

        return ret

    elif status == 'new':
        ip_adsl = request.args['ip_adsl']
        ip_idc = request.remote_addr

        adsl.additem(lines, ip_idc, ip_adsl)

        str = lines + ':' + ip_idc + ':' + ip_adsl

        return 'Add ' + str + ' successfully!'


if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
