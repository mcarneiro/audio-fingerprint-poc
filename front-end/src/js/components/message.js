export default function messageBy($feedback) {
  return msg => {
    $feedback.innerText = msg
    if (msg !== '') {
      $feedback.classList.add('-active')
    } else {
      $feedback.classList.remove('-active')
    }
  }
}
