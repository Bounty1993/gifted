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

let messageForm = document.getElementById('messageForm')
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

function makeGuestList(data) {
    questList = document.getElementById('guestList')
    guestList.innerHTML = ''
    for (let guest of data) {
        listItem = document.createElement('li')
        listItem.classList.add('list-group-item', 'list-group-item-action')
        listItem.textContent = guest
        guestList.append(listItem)
    }
}

let addGuest = document.getElementById('addGuest')
addGuest.onclick = () => {
    let type = 'add'
    let guest = document.getElementById('guestInput').value
    let data = {type: type, guest: guest}
    let url = '/rooms/1/ajax/guests/'
    let ajax = post_fetch(url, data).then(response => response.json())
    ajax.then(response => {
        guests = response['guests']
        makeGuestList(guests)
    })
}

let removeGuest = document.getElementById('removeGuest')
removeGuest.onclick = () => {
    let type = 'remove'
    let guest = document.getElementById('guestInput').value
    let data = {type: type, guest: guest}
    let url = '/rooms/1/ajax/guests/'
    let ajax = post_fetch(url, data).then(response => response.json())
    ajax.then(response => {
        guests = response['guests']
        makeGuestList(guests)
    })
}
