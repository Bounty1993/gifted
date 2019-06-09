function makeProgressBar(progress) {
    progressBar = document.getElementById('progressBar')
    progressBar.style.width = `${progress}%`
}

supportBtn = document.getElementById('supportBtn')
supportBtn.onclick = () => {
  supportForm = document.getElementById('supportForm')
  supportForm.classList.toggle('hidden')
}

submitSupport = document.getElementById('submitSupport')
submitSupport.onclick = (event) => {
  amount = document.getElementById('amount')
  comment = document.getElementById('comment')
  data = {
    amount: amount.value,
    comment: comment.value
  }
  url = `/rooms/1/ajax/donate/`
  ajax = post_fetch(url, data).then(response => response.json())
  ajax.then(response => {
    message = response['message']
    if (message==='Success') {
        window.location.reload()
    } else {
        if (message['amount']) {
            amount_error = document.createElement('div')
            amount_error.textContent = message['amount']
            amount.after(amount_error)
        }
    }
  })
}

messageForm = document.getElementById('messageForm')
messageForm.onsubmit = (event) => {
    event.preventDefault()
    let receiver = event.target.receiver.value
    let subject = event.target.subject.value
    let content = event.target.content.value
    data = {receiver: receiver, subject: subject, content: content}
    url = '/rooms/ajax/message/'
    ajax = post_fetch(url, data).then(response => response.json())
    ajax.then(response => {
        if (response['is_valid'] === 'true') {
            successMsg = makeMessage('success', 'Wiadomość została wysłana')
            event.target.receiver.before(successMsg)
        } else {
            failureMsg = makeMessage('danger', 'Dane są błęde')
            event.target.receiver.before(failureMsg)
        }
    })
}




