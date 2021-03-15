import json
import base64
import logging
from pydub import AudioSegment
from recognize_from_file import run_recognition

def handler(event, context):
  fh = open('/tmp/audio.ogg', 'wb')
  fh.write(base64.b64decode(json.loads(event['body'])['data']))
  fh.close()

  AudioSegment.from_file('/tmp/audio.ogg').export('/tmp/audio.mp3',
    format='mp3',
    bitrate='128k',
    parameters= ['-ac', '2', '-ar', '44100'])

  print('run recognition')
  song = run_recognition('/tmp/audio.mp3')
  print('results', song)

  return {
    'statusCode': 200,
    'headers': {
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    },
    'body': json.dumps(song)
  }


if __name__ == '__main__':

  f = open('input-audios/quero-cafe-2-sons-5s.m4a.base64', 'r')
  mp3base64 = f.read()
  f.close()

  # Run recognition
  lambda_handler(
    event = {
      'body': mp3base64
    },
    context = None
  )
