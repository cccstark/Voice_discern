#上传分为两种方式：隐式上传和显式上传
#隐式上传：Json方式上传
#显式上传:Raw方式上传

#sudo apt-get install portaudio19-dev python-all-dev python3-all-dev
#pip install pyaudio

import pyaudio
import wave
import requests
import json
import base64
import os


#1.录音
#用Pyaudio录制音频(该库可以进行录音,播放,生成wav文件)
def audio_record(rec_time,filename):
    """
    :param rec_time: 音频录制时间
    :param filename: 输出音频文件名
    """
    CHUNK=1024#定义数据流块
    FORMAT=pyaudio.paInt16#16bit编码格式
    CHANNELS=1#单声道
    RATE=16000#16000采样频率
    #创建一个音频对象
    p=pyaudio.PyAudio()
    #创建音频数据流
    stream=p.open(format=FORMAT,#音频流wav格式
                  channels=CHANNELS,#单声道
                  rate=RATE,#采样率16000
                  input=True,#输入
                  frames_per_buffer=CHUNK)
    print('start recording...')
    frames=list()#空列表用于保存录制的音频流
    #录制音频数据
    for i in range(0,int(RATE/CHUNK*rec_time)):
        data=stream.read(CHUNK)
        frames.append(data)
    #录制完成
    print(frames)
    #停止数据流
    stream.stop_stream()
    stream.close()
    #关闭pyaudio
    p.terminate()
    print('recording done...')
    #保存音频文件
    with wave.open(filename,'wb') as f:
        f.setnchannels(CHANNELS)#设置音频声道数
        f.setsampwidth(p.get_sample_size(FORMAT))#以字节为单位返回样本宽度
        f.setframerate(RATE)#设置取样频率
        f.writeframes(b''.join(frames))

    #return filename#返回文件名

#2 使用appKey secretKey 访问 https://openapi.baidu.com 换取 token
def Get_token():
    #baidu_server='https://openapi.baidu.com/oauth/2.0/token'
    grant_type = 'client_credentials'
    # API KEY
    client_id = 'PrKnhUppGEsqrG8mVG2qIq8O'
    # SECRERT KEY
    client_secret = 'Al4cRfrlRGaMCCkz3kLsd4MXOoQP28iD'

    # 拼接url
    url = 'https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(
            client_id, client_secret)
    # 发送Post请求　获取acess_token
    req = requests.post(url)
    data_dict = json.loads(req.text)  # 将json字符串转换为python字典
    print(req.text)
    print(data_dict['access_token'])

    return data_dict['access_token']

#3.上传录音文件
def BaiduYuYin(file_url,token):
    try:
        RATE='16000'
        FORMAT='wav'
        CUID='wate_play'
        DEV_PID='1536' #普通话：支持简单的英文识别

        file_url=file_url
        token = token

        #以字节格式读取文件之后进行编码
        with open(file_url,'rb') as f:
            speech=base64.b64encode(f.read()).decode('utf-8')
        size = os.path.getsize(file_url)#语音文件的字节数
        headers={'Content-Type':'application/json'}#json格式post上传本地文件
        url='https://vop.baidu.com/server_api'
        data={
            "format":FORMAT,#格式
            "rate":RATE,#取样频率,固定值16000
            "dev_pid":DEV_PID,#语音识别类型
            "speech":speech,#本地语音文件的二进制数据,需要进行base64编码
            "cuid":CUID,#用户唯一标识,用来区分用户 建议填写能区分用户的机器MAC地址或IMEI码,长度为60字符以内。
            "len":size,#语音文件的字节数
            "channel":1,#声道数,仅支持单声道,固定值为1
            "token":token,
        }
        req=requests.post(url,json.dumps(data),headers)
        data_dict=json.loads(req.text)
        print(data_dict['result'][0])
        return data_dict['result'][0][::-1]
    except:
        return '识别不清楚'

#4.调度
def run(rec_time,file_name):
    #1.录音
    audio_record(rec_time,file_name)

    #2.获取token
    access_token=Get_token()

    #3.上传录音
    BaiduYuYin(file_name,access_token)


if __name__ == '__main__':
    #录音时间为5秒,文件名为'record1.wav'
    run(5,'record1.wav')