import os
import sys
import json
import subprocess
import platform
from datetime import datetime

pltfrm = platform.system().lower()

if pltfrm == 'windows':
  basedir = 'c:/windows/temp'
elif pltfrm == 'linux' or pltfrm == 'darwin':
  basedir = '/tmp'
else:
  print(f'Unsupported platform: {pltfrm}')
  sys.exit(1)
 
fio_testfile = os.path.join(basedir, 'fio_raw_data')
fio_output_file = os.path.join(basedir, 'out.json')
fio_job_file = os.path.join('jobs', f'{pltfrm}.fio')
facility = 'nectar'

def delete_fio_files():
  if os.path.exists(fio_testfile):
    os.remove(fio_testfile)
  if os.path.exists(fio_output_file):
    os.remove(fio_output_file)

def run_fio():
  cmd_array = ["fio", "--output-format", "json", '--output', fio_output_file, '--filename', fio_testfile, fio_job_file] 
  proc = subprocess.run(
    cmd_array,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
  )

  if proc.returncode != 0:
    print(proc.stderr)
  return proc.returncode


def print_fio_results():
  with open(fio_output_file, 'r') as f:
    data = json.load(f)
  fio_version = data['fio version']
  timestamp = data['timestamp']
  date_time = datetime.fromtimestamp(timestamp)
  global_options = data['global options']
  ioengine = data['global options']['ioengine']
  del global_options['ioengine']
  del global_options['filename']

  for job in data['jobs']:
    job_type = job['job options']['rw']
    bs = job['job options']['bs']
    iodepth = job['job options']['iodepth']
    del job['job options']['rw']
    del job['job options']['bs']
    del job['job options']['iodepth']
    job_options = {**global_options, **job['job options']}
    print(f'{date_time} | {facility} | {pltfrm} | {job_type} | {ioengine} | {bs} | {iodepth} | {job_options}')
    for x in ['read', 'write']:
      if job[x]['io_bytes'] > 0:
        iops = job[x]['iops'] 
        bw_mbps = job[x]['bw']
        print(x + ' BW: ' + str(bw_mbps) + ' KB/s')
        print(x + ' IOPS: ' + str(iops))
    print()

delete_fio_files()
run_fio()
print_fio_results()
delete_fio_files()
