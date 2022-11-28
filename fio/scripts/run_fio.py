import os
import sys
import json
import subprocess
import platform
import tempfile
import configparser
import pymysql.cursors

pltfrm = platform.system().lower()
if pltfrm != 'windows' and pltfrm != 'linux' and pltfrm != 'darwin':
    print(f'Unsupported platform: {pltfrm}')
    sys.exit(1)

config = configparser.ConfigParser()
config.read('config.ini')
facility = config['main']['facility']

basedir = tempfile.gettempdir()
fio_testfile = os.path.join(basedir, 'fio_raw_data')
fio_output_file = os.path.join(basedir, 'out.json')
fio_job_file = os.path.join('jobs', f'{pltfrm}.fio')

db_conn = pymysql.connect(host=config['mysql']['host'],
                          port=int(config['mysql']['port']),
                          user=config['mysql']['user'],
                          password=config['mysql']['password'],
                          database=config['mysql']['database'],
                          cursorclass=pymysql.cursors.DictCursor)


def delete_fio_files():
    for name in [fio_testfile, fio_output_file]:
        if os.path.exists(name):
            os.remove(name)


def run_fio():
    cmd_array = ["fio", "--output-format", "json", '--output', fio_output_file, '--filename', fio_testfile,
                 fio_job_file]
    proc = subprocess.run(
        cmd_array,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if proc.returncode != 0:
        raise Exception(proc.stderr)

    return proc.returncode


def store_fio_results():
    with open(fio_output_file, 'r') as f:
        data = json.load(f)
    timestamp = data['timestamp']
    global_options = data['global options']

    with db_conn.cursor() as cursor:
        for job in data['jobs']:
            job_options = {**global_options, **job['job options']}
            sql = "INSERT INTO `fio_benchmarks` (`timestamp`, `facility`, 'platform', " \
                  "'config', 'bw_read_kbs', 'iops_read', 'bw_write_kbs', 'iops_write') " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (timestamp, facility, pltfrm, job_options, job['read']['bw'],
                                 job['read']['iops'], job['write']['bw'], job['write']['iops']))


delete_fio_files()
try:
    run_fio()
    store_fio_results()
finally:
    delete_fio_files()
