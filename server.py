from flask import Flask, request, Response, g
#from flask_socketio import SocketIO
from functools import wraps
import json
import os
import subprocess
import time
import signal
import glob
import datetime

app = Flask(__name__)
#sio = SocketIO(app)

pid = None
PIPE_PATH = '/home/x300/eclipse-workspace/Spectrum/Release/Statuses.txt'
DATA_FILE='/home/x300/eclipse-workspace/Spectrum/Release/*.dat'
DATA_PATH='/home/x300/eclipse-workspace/Spectrum/Release'
PLAY='/home/x300/eclipse-workspace/Spectrum/Release/Spectrum --mode play'
RECORD='/home/x300/eclipse-workspace/Spectrum/Release/Spectrum --mode record'
SPECTRUM='/home/x300/eclipse-workspace/Spectrum/Release/Spectrum --mode spec'
RATE = str(100e6)

def json_input(f):
    @wraps(f)
    def json_input_wrapper(*a, **kw):
        if request.data and request.headers['Content-Type'] == 'application/json':
            try:
                g.json = json.loads(request.data)
            except ValueError:
                return Response('Bad JSON', 400)
        ret = f(*a, **kw)
        return ret
    return json_input_wrapper


def json_output(f):
    @wraps(f)
    def json_output_wrapper(*a, **kw):
        ret = f(*a, **kw)
        resp = Response(json.dumps(ret, separators=(',', ':')))
        resp.mimetype = 'application/json'
        return resp
    return json_output_wrapper


@app.route('/work', methods=['POST'])
@json_input
def work():
    global pid
    params = request.json
    
    kill()

    if not pid:
        # os.remove(PIPE_PATH)
        
        F0,Q = getFo_and_Q(params)
        if params['play'] == True:
            #"--mode play --freq " + f0.ToString() + " --rate " + Rate.ToString() + " --gain " + Gain.ToString() + " --file " + CurrFile + LoopMode;
            cmd = '%s --freq %s --rate %s --gain %s --file %s' % (PLAY, F0, RATE, params['agc'], params['Filename'])
            if 'loop' in params:
                if params['loop'] == 'on':
                    cmd = '%s --loop' % cmd
        else:
            if params['agc_auto'] == True:
                params['agc'] = '-1';
                
            if params['mode'] == 'record':
                timeString =  datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                recordfile = '%s/%s-%s-%s-%s.dat' % (DATA_PATH,timeString,F0,Q, params['agc'])
                # "--mode record --freq " + f0.ToString() + " --rate " + Rate.ToString() + " --gain " + Gain.ToString() + " --file " + CurrFile + " --nsamps " + NumSamples.ToString();
                cmd = '%s --ferq %s --rate %s --gain %s --file %s --samps %s' % (RECORD, F0, RATE, params['agc'],recordfile, str(1000000))
            else:
                recordfile = '%s/%s.dat'%  (DATA_PATH,'spectrum.dat')
                cmd = '%s --rate %s --file %s' % (SPECTRUM, RATE, recordfile)
        # p = subprocess.Popen('ping %s > %s' % (g.json['host'], PIPE_PATH), shell=True)
        # pid = p.pid
        pid = 0
        print cmd
        time.sleep(.5)

    def worker():
        with open(PIPE_PATH) as f:
            while p.poll() is None:  # Only works on Linux
                time.sleep(.1)
                try:
                    yield f.read()
                except Exception as e:
                    print '%s: %s' % (e.__class__.__name__, e)

    #return Response(worker(), mimetype='text/plain')
    return Response('OK', mimetype='text/plain')

def getFo_and_Q(d):
    F0 = 10
    Q = 1
    if d['freq_center'] == True:
        F0 = d['center_freq']
        Q = d['rec_bandwidth']
    else:
        F0 =  str(int(d['low_freq']) + ((int(d['high_freq']) -  int(d['low_freq']))/2))
        Q = str((int(d['high_freq']) -  int(d['low_freq']))/2)
    return F0, Q


    

@app.route('/kill')
def kill():
    global pid
    if not pid:
        return 'Already dead'
    os.kill(pid, signal.SIGKILL)
    pid = None
    return 'Killed'


@app.route('/pid')
def get_pid():
    return str(pid)


@app.route('/file_list')
@json_output
def file_list():
    return glob.glob (DATA_FILE)


@app.route('/')
def index():
    return open('recorder.html').read()


def main():
    app.run('0.0.0.0', 12345, debug=True)


if __name__ == '__main__':
    main()
