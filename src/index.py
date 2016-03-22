# -*- coding: utf-8 -*-


from flask import Flask, request, url_for, redirect
import MySQLdb


app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for('adsllist'))


@app.route('/adsl/list', methods=['GET', 'POST'])
def adsllist():
    conn = MySQLdb.connect(host='192.168.27.37', user='root', passwd='root', db='CDB', charset='utf8')
    cur = conn.cursor()

    if request.method == 'GET':
        parameters = request.args
        getline = lambda x: x[0]
        lines = []
        if len(parameters) > 0:
            if 'num' in parameters:
                num = parameters['num']
                sql = 'select line,ip_adsl,status from tb_adsl where status="available" limit ' + num
                cur.execute(sql)
                data = cur.fetchall()
                print data
                for ret in data:
                    lines.append(getline(ret))

                print lines
                if len(lines) > 1:
                    sql = 'update tb_adsl set status="using" where line in ' + str(tuple(lines)).replace('u\'', '\'')
                if len(lines) == 1:
                    sql = 'update tb_adsl set status="using" where line=\'' + str(lines[0]) + '\''

                cur.execute(sql)
                conn.commit()
            elif 'show' in parameters:
                if parameters['show'].lower() == 'all':
                    sql = 'select line,ip_adsl,status from tb_adsl'
                    cur.execute(sql)
                    data = cur.fetchall()

        else:
            sql = 'select line,ip_adsl,status from tb_adsl where status="available"'
            cur.execute(sql)
            data = cur.fetchall()

    lines = []
    for ret in data:
        lines.append(str(ret))

    rets = '\n'.join(lines).replace('u\'', '').replace('\'', '').replace('(', '').replace(')', '')\
        .replace(',', ':').replace(' ', '')

    cur.close()
    conn.close()

    return str(rets)


@app.route('/adsl', methods=['POST'])
def adslop():
    conn = MySQLdb.connect(host='192.168.27.37', user='root', passwd='root', db='CDB', charset='utf8')
    cur = conn.cursor()
    rets = 1
    parameters = request.form
    lines = parameters['lines']

    try:
        lines_f = []
        if ',' in lines:
            for line in lines.split(','):
                lines_f.append(line)
                sql = 'update tb_adsl set status="dailing" where line in ' + str(tuple(lines_f)).replace('u\'', '\'')
        else:
            sql = 'update tb_adsl set status="using" where line=\'' + lines + '\''
        cur.execute(sql)

        conn.commit()
    except MySQLdb.Error:
        rets = 0

    cur.close()
    conn.close()

    return str(rets)


if __name__ == '__main__':
    app.run(debug=True, port=8000, host='192.168.27.37')