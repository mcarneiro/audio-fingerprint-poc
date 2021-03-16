import 'regenerator-runtime/runtime'

import recorderFor from './components/recorder'
import messageBy from './components/message'
import loaderAnimation from './components/loader-animation'

const button = document.querySelector('button')

const api = __API__
const $feedback = document.querySelector('#feedback')
const recordingTime = 5500
const IS_DEBUG = document.location.hash === '#debug'

const message = messageBy($feedback)
const recorder = recorderFor(recordingTime)

function startRecording() {
  if (button.classList.contains('-disabled')) {
    return
  }
  message('')
  button.classList.add('-disabled')

  recorder.start()
    .catch(message)

  loaderAnimation(document.querySelector('#timerIndicator'), recordingTime, 660)

  recorder.getAudio()
    .then(({blob, base64}) => {
      if (IS_DEBUG) {
        const player = new Audio(URL.createObjectURL(blob))
        player.controls = true
        document.querySelector('#debug').appendChild(player)
      }

      message('Processando...')

      fetch(api + '?_u=' + Date.now(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
          // Local docker behaves and expect data differently and will return nothing, so it'll throw a cors error,
          // but data will be sent to the server and you can check it on the server output
          // 'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: JSON.stringify({data: base64.split('base64,').pop()})
      })
      .then(res => res.json())
      .then(data => {
        button.classList.remove('-disabled')
        if (data.CONFIDENCE > 4) {
          message(`Achou o cupom ${data.SONG_NAME.split('.')[0]}!`)
        } else {
          message(IS_DEBUG ? JSON.stringify(data) : 'Não foi dessa vez! Garanta que o microfone não esteja coberto ou que o volume não esteja muito baixo.')
        }
      })
      .catch(message)
    })
}

button.addEventListener('click', startRecording)
