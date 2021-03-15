import QRCode from 'qrcode'

QRCode.toDataURL(document.location.protocol + '//' + document.location.host + '/index.html')
  .then(url => {
    document.querySelector('#qrCode').setAttribute('src', url)
  })
