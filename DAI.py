import os, sys, time, json
from datetime import datetime
import paho.mqtt.client as mqtt

sys.path.insert(0, '/usr/lib/python2.7/bridge/')
from bridgeclient import BridgeClient

import DAN
import config

odf_list = getattr(config,'odf_list', [])
idf_list = getattr(config,'idf_list', [])
broker = getattr(config,'MQTT_broker', None)
mq_port = getattr(config,'MQTT_port', 1883)
mq_usr = getattr(config,'MQTT_User', None)
mq_pw = getattr(config,'MQTT_PW', None)
device_id = DAN.get_mac_addr()
DAN.profile['dm_name'] = config.dm_name
if not config.d_name: DAN.profile['d_name'] = '{}.{}'.format(config.dm_name, DAN.get_mac_addr()[-4:])
else: DAN.profile['d_name'] = config.d_name
if broker: DAN.profile['mqtt_enable'] = True
DAN.profile['df_list'] = [t[0] for t in idf_list]
for t in odf_list:
    if t[0] not in DAN.profile['df_list']:
        DAN.profile['df_list'].append(t[0])
print('Detected features:')
for f_name in DAN.profile['df_list']:
    print('    {}'.format(f_name))

Bclient = BridgeClient()
def LED_flash(LED_state):
    if LED_state:
        Bclient.put('Reg_done', '1')
        os.system(r'echo "timer" > /sys/class/leds/ds:green:usb/trigger')      #For ArduinoYun Only. LED Blink.
    else:
        Bclient.put('Reg_done', '0')
        os.system(r'echo "none" > /sys/class/leds/ds:green:usb/trigger')

def on_connect(client, userdata, flags, rc):
    if not rc:
        print('MQTT broker: {}'.format(broker))
        LED_flash(1)
        if odf_list == []:
            print('ODF list is empty.')
            return
        topic_list=[]
        for odf in odf_list:
            topic = '{}//{}'.format(device_id, odf[0])
            topic_list.append((topic,0))
        if topic_list != []:
            r = client.subscribe(topic_list)
            if r[0]: print('Failed to subscribe topics. Error code:{}'.format(r))
            else: print('Subscribe:', topic_list)
    else: print('Connect to MQTT borker failed. Error code:{}'.format(rc))
        
def on_disconnect(client, userdata,  rc):
    print('MQTT Disconnected. Re-connect...')
    LED_flash(0)
    client.reconnect()

def on_message(client, userdata, msg):
    os.system(r'echo "default-on" > /sys/class/leds/ds:green:wlan/trigger')
    samples = json.loads(msg.payload)
    odf = msg.topic.split('//')[1]
    data = samples['samples'][0][1]
    ###ODFdir{'f_name': ('pin_name', index)}### just note
    print('{}: {}, {}'.format(samples['samples'][0][0], ODFdir[odf][0], str(int(data[ODFdir[odf][1]]))))
    Bclient.put(ODFdir[odf][0], str(int(data[ODFdir[odf][1]])))
    os.system(r'echo "none" > /sys/class/leds/ds:green:wlan/trigger')

def mqtt_pub(client, deviceId, IDF, data):
    topic = '{}//{}'.format(deviceId, IDF)
    if type(data) is not list: data = [data]
    sample = [str(datetime.today()), data]
    payload  = json.dumps({'samples':[sample]})
    status = client.publish(topic, payload)
    if status[0]: print('topic:{}, status:{}'.format(topic, status))

def MQTT_config(client):
    client.username_pw_set(mq_usr, mq_pw)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.connect(broker, mq_port, keepalive=60)

DAN.device_registration_with_retry(config.ServerURL)
LED_flash(1)

if broker:
    ODFdir={}
    for f_name, index, pin_name in odf_list:
        ODFdir[f_name] = (pin_name, index)
    mqttc = mqtt.Client()
    MQTT_config(mqttc)
    mqttc.loop_start()

incomming = {}
for f_name in [t[0] for t in odf_list]:
    incomming[f_name] = 0

if idf_list == []: print('IDF list is empty.')
reConnecting = 0
while True:
    try:
        for f_name, type_ in idf_list:
            tmp = Bclient.get(f_name)
            if tmp is None:
                continue            
            else: 
                Bclient.delete(f_name)    

            v = type_(tmp)
            if v is not None:
                os.system(r'echo "default-on" > /sys/class/leds/ds:green:wlan/trigger')
                if broker:
                    mqtt_pub(mqttc, device_id, f_name, v)
                else:
                    DAN.push(f_name, v)
                print '{t}: Push({f}, {v!r})'.format(t=datetime.today(), f=f_name, v=v)
                os.system(r'echo "none" > /sys/class/leds/ds:green:wlan/trigger')

        if broker: 
            time.sleep(config.Comm_interval)
            continue        
        cache = {}
        check_list=[t[0] for t in odf_list]
        for f_name, index, pin_name in odf_list:
            if f_name not in cache.keys():
                os.system(r'echo "default-on" > /sys/class/leds/ds:green:wlan/trigger')
                PIN = DAN.pull(f_name)
                cache[f_name] = PIN
            else:
                    PIN = cache[f_name]

            if PIN != None:
     
                check_list.remove(f_name)

                if PIN[index] != None:
                    Bclient.put(pin_name, str(int(PIN[index])))
                else: 
                    continue
                
                if f_name not in check_list:
                    incomming[f_name] = (incomming[f_name] + 1) % 10000

                print '{f}[{d}] -> {p} = {v}, incomming[{f}] = {i}'.format(
                        f=f_name,
                        d=index,
                        p=pin_name,
                        v=str(int(PIN[index])),
                        i=incomming[f_name],
                )
            os.system(r'echo "none" > /sys/class/leds/ds:green:wlan/trigger')

        if reConnecting:
            LED_flash(1)
            reConnecting = 0    
    
    except Exception, e:
        print(e)
        LED_flash(0) 
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            reConnection = 1
            DAN.device_registration_with_retry(config.ServerURL)
        else:
            print('Connection failed due to unknow reasons.')
            reConnecting = 1
            time.sleep(1)    
            
    time.sleep(config.Comm_interval)
