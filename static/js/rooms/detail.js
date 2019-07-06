let room_id = window.location.pathname.split('/')[2]

let socketUrl = 'ws://' + window.location.host + '/' + 'ws/room/' + room_id + '/donate/'
console.log(socketUrl)
let roomSocket = new WebSocket(socketUrl)

roomSocket.onmessage = (e) => {
    let data = JSON.parse(e.data)
    console.log(data)
}

roomSocket.onclose = (e) => {
    console.error('Socket is closed')
}

// function draws a nice progress bar showing how much money has been already collected
function makeProgressRoom(progress) {
    progressRoom = document.getElementById('progressRoom')
    console.log(progress)
    progressRoom.style.width = `${progress}%`
}

// function makes a support form toggling
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
  console.log(room_id)
  /*
  url = `/rooms/${room_id}/ajax/donate/`
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
  */
  roomSocket.send(JSON.stringify(data))
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

makeProgressRoom(progress)

// function responsible for adding guest watching the room.
// only the creator can do that in 'rooms:edit'
let addGuest = document.getElementById('addGuest')
addGuest.onclick = () => {
    let type = 'add'
    let guest = document.getElementById('guestInput').value
    let data = {type: type, guest: guest}
    let url = `/rooms/${room_id}/ajax/guests/`
    let ajax = post_fetch(url, data).then(response => response.json())
    ajax.then(response => {
        guests = response['guests']
        makeGuestList(guests)
    })
}

// function responsible for removing guest watching the room.
// only the creator can do that in 'rooms:edit'
let removeGuest = document.getElementById('removeGuest')
removeGuest.onclick = () => {
    let type = 'remove'
    let guest = document.getElementById('guestInput').value
    let data = {type: type, guest: guest}
    let url = `/rooms/${room_id}/ajax/guests/`
    let ajax = post_fetch(url, data).then(response => response.json())
    ajax.then(response => {
        guests = response['guests']
        makeGuestList(guests)
    })
}
