export default function recorderFor(recordingTime = Infinity) {
  const chunks = []
  const connect = (() => {
    let promise
    return () => {
      if (promise) {
        return promise
      }
      return promise = new Promise((ok, fail) => {
        const onSuccess = (stream) => {
          const mediaRecorder = new MediaRecorder(stream)

          mediaRecorder.addEventListener('dataavailable', e => {
            chunks.push(e.data)
          })

          stream.addEventListener('inactive', e => {
            promise = null
          })

          ok({
            mediaRecorder,
            stream,
            chunks: () => chunks.concat()
          })
        }

        navigator.mediaDevices.getUserMedia({ audio: true })
          .then(onSuccess)
          .catch(fail)
      })
    }
  })()

  const timeout = (() => {
    let t

    return () => {
      clearTimeout(t)
      t = setTimeout(stop, recordingTime)
    }
  })()

  const onDataAvailable = e => {
    chunks.push(e.data)
  }

  const toBase64 = blob => new Promise((ok, fail) => {
    const reader = new FileReader()
    reader.readAsDataURL(blob)
    reader.onload = (e) => ok(e.target.result)
    reader.onerror = fail
  })

  const reset = async () => {
    const {mediaRecorder} = await connect()
    chunks.length = 0
    if (onStopRecordingPromise) {
      mediaRecorder.removeEventListener('stop', onStopRecordingPromise)
    }
    mediaRecorder.removeEventListener('dataavailable', onDataAvailable)
  }

  const start = async () => {
    reset()
    const {mediaRecorder} = await connect()
    mediaRecorder.addEventListener('dataavailable', onDataAvailable)
    mediaRecorder.start()
    if (recordingTime < Infinity) {
      timeout()
    }
  }

  const stop = async () => {
    const {mediaRecorder, stream} = await connect()
    mediaRecorder.stop()
    stream.getTracks().forEach(track => track.stop())
  }

  const onStopRecording = (ok, fail) => () => {
    try {
      const blob = new Blob(chunks, { 'type' : 'audio/ogg codecs=opus' })
      toBase64(blob)
        .then((base64) => ok({blob, base64}))
        .catch(fail)
    } catch(e) {
      fail(e)
    }
  }
  let onStopRecordingPromise

  const getAudio = async () => {
    const {mediaRecorder} = await connect()
    return new Promise((ok, fail) => {
      onStopRecordingPromise = onStopRecording(ok, fail)
      mediaRecorder.addEventListener('stop', onStopRecordingPromise)
    })
  }

  return { start, stop, getAudio, connect }
}
