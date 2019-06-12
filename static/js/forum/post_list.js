function handleRespond(event) {
    let comment = event.target.closest('.comment')

    let form = document.createElement('div')
    form.dataset.post = comment.dataset.post
    form.classList.add('comment', 'thread')

    let subjectInput = document.createElement('input')
    subjectInput.classList.add('form-control')
    subjectInput.placeholder = 'Tytuł'
    subjectInput.name = 'subject'

    let contentInput = document.createElement('input')
    contentInput.classList.add('form-control','mt-2')
    contentInput.placeholder = 'Treść'
    content.name = 'content'

    let sendBtn = document.createElement('button')
    sendBtn.classList.add('forumBtn', 'mainBtn', 'mt-2')
    sendBtn.textContent = 'Wyślij odpowiedź'
    sendBtn.addEventListener('click', handleSubmit)

    form.append(subjectInput, contentInput, sendBtn)
    comment.after(form)

}

function handleSubmit(event) {
    let comment = event.target.closest('.comment')
    let parentId = comment.dataset.post
    if (!parentId) {
        parentId = comment.datset.thread
    }
    let subject = comment.children[0].value
    let content = comment.children[1].value
    data = {
        parentId: parentId,
        subject: subject,
        content:content
    }
    roomSocket.send(JSON.stringify(data))

    comment.remove()
    // url = `/forum/ajax/thread/create/`
    // ajax = post_fetch(url, data).then(response => response.json())
    // ajax.then(response => {
    //    console.log(response)
    //})
}

let makeThread = (data) => {
    parentId = data.parentId
    console.log(data)

    let comments = document.querySelector(`[data-post="${data.post}"]`)
    console.log(comments)
    let thread = document.createElement('div')
    thread.dataset.thread = data['id']
    thread.classList.add('comment', 'thread')

    let head = document.createElement('div')
    head.classList.add('head')

    for (let attr of ['author', 'likes', 'date']) {
        let elem = document.createElement('span')
        elem.textContent = data[attr]
        head.append(elem)
    }

    thread.append(head)

    let text = document.createElement('div')
    for (let attr of ['subject', 'content']) {
        let elem = document.createElement('div')
        elem.textContent = data[attr]
        text.append(elem)
    }
    thread.append(text)

    let commentBtns = document.createElement('div')
    commentBtns.classList.add('commentBtns', 'clearfix')

    let dislikeBtn = document.createElement('button')
    dislikeBtn.classList.add('right', 'dislikeBtn', 'myBtn')
    dislikeBtn.textContent = 'Nie lubię'

    let likeBtn = document.createElement('button')
    likeBtn.classList.add('right', 'likeBtn', 'myBtn')
    likeBtn.textContent = 'Lubię'

    commentBtns.append(dislikeBtn)
    commentBtns.append(likeBtn)
    thread.append(commentBtns)

    console.log(thread)

    comments.after(thread)

}

let respondBtns = document.querySelectorAll('.respondBtn')
let likeBtns = document.querySelectorAll('.likeBtn')
let dislikeBtns = document.querySelectorAll('.dislikeBtn')
console.log(dislikeBtns)
for (let i=0; i < respondBtns.length; i++) {
    respondBtns[i].addEventListener('click', handleRespond)
    likeBtns[i].addEventListener('click', handleLike)
    dislikeBtns[i].addEventListener('click', handleDislike)
}

// ---------------------WebSockets---------------------------
let window_url = window.location.href.split('/')
let room_name = window_url[window_url.length -2]
let socket_url = 'ws://' + window.location.host + '/' + 'ws/room/' + room_name + '/post/'
let roomSocket = new WebSocket(socket_url)

roomSocket.onmessage = (e) => {
    let data = JSON.parse(e.data)
    makeThread(data)
}
roomSocket.onclose = (e) => {
    console.error('Socket is closed')
}

//------------------------------------------------------------