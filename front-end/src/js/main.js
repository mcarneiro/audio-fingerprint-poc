const button = document.querySelector('button')

const api = __API__
const $feedback = document.querySelector('#feedback')
const recordingTime = 5500

const toBase64 = file => new Promise((resolve, reject) => {
  const reader = new FileReader()
  reader.readAsDataURL(file)
  reader.onload = () => resolve(reader.result)
  reader.onerror = error => reject(error)
})

const message = msg => {
  $feedback.innerText = msg
  if (msg !== '') {
    $feedback.classList.add('-active')
  } else {
    $feedback.classList.remove('-active')
  }
}

function startRecording() {
  if (button.classList.contains('-disabled')) {
    return
  }
  message('')
  button.classList.add('-disabled')

  if (navigator.mediaDevices.getUserMedia) {
    let chunks = []

    let onSuccess = function(stream) {
      const mediaRecorder = new MediaRecorder(stream)

      mediaRecorder.addEventListener('stop', e => {
        const blob = new Blob(chunks, { 'type' : 'audio/ogg codecs=opus' })
        chunks = []

        if (document.location.hash === '#debug') {
          const player = new Audio(URL.createObjectURL(blob))
          player.controls = true
          $feedback.appendChild(player)
        }
        message('Processando...')

        var reader = new FileReader()
        reader.readAsDataURL(blob)
        reader.onloadend = function() {
          var data = reader.result

          fetch(api + '?_u=' + Date.now(), {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
              // 'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: JSON.stringify({data: data.split('base64,').pop()})
            // body: JSON.stringify({body: {data: data.split('base64,').pop()}})
          })
          .then(res => res.json())
          .then(data => {
            button.classList.remove('-disabled')
            if (data.CONFIDENCE > 1 && data.OFFSET_SECS > 0) {
              message(`Achou o cupom ${data.SONG_NAME.split('.')[0]}!`)
            } else {
              message('Não foi dessa vez!')
            }
          })
          .catch(message)
        }
      })

      mediaRecorder.addEventListener('dataavailable', e => {
        chunks.push(e.data)
      })

      mediaRecorder.start()
      const start = Date.now()

      const circle = document.querySelector('#timerIndicator')
      const tick = () => {
        const now = Date.now()
        let diff = (now - start) / recordingTime

        circle.setAttribute("stroke-dasharray", (Math.min(diff, 1) * 660) + ", 20000")
        if (diff <= 1) {
          requestAnimationFrame(tick)
        }
      }
      tick()

      setTimeout(() => {
        mediaRecorder.stop()
        stream.getTracks().forEach(track => track.stop())
      }, recordingTime)
    }

    let onError = function(err) {
      message('Ocorreu um erro: ' + err)
    }

    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(onSuccess)
      .catch(onError)

  } else {
    message('Seu navegador não suporta o uso do microfone.')
  }
}

button.addEventListener('click', startRecording)
