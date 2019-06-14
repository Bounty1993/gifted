function handleRespond(event) {
    let comment = event.target.closest('.comment')

    let form = document.createElement('div')
    form.dataset.post = comment.dataset.post
    form.classList.add('comment')

    let commentMargin = window.getComputedStyle(comment).getPropertyValue('margin-left')
    let newMargin = parseInt(commentMargin, 10) + 20
    form.style.marginLeft = newMargin + 'px'

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
let getThreads = (event) => {
    let comment = event.target.closest('.comment')
    let post_id = comment.dataset.post
    if (post_id) {
        data = {post_id: post_id}
    } else {
        data = {'thread_id': comment.dataset.thread}
    }
    url = `ajax/thread/list/`
    ajax = post_fetch(url, data).then(res => res.json())
    ajax.then(response => {
        if (response['is_valid'] === 'true') {
            threads = response['threads']

            for (let thread of Object.values(threads)) {
                makeThread(thread)
            }
        }
    })
    event.target.disabled = true
}

let manageLikeBtn = (comment) => {
    let likeBtn = comment.querySelector('.likeBtn')
    likeBtn.disabled = true
    likeBtn.style.background = 'green'
    likeBtn.textContent = 'Dziękujemy za głos'
    let dislikeBtn = comment.querySelector('.dislikeBtn')
    dislikeBtn.remove()
}

let handleLike = (event) => {
    let comment = event.target.closest('.comment')
    let id = comment.dataset.post || comment.dataset.thread
    let is_thread = comment.dataset.thread ? 'true': null
    let data = {
        id: id,
        is_thread: is_thread,
    }
    let url = '/forum/ajax/like/'
    ajax = post_fetch(url, data).then(res => res.json())
    ajax.then(res => {
        num_likes = res['num_likes']
        comment.querySelector('[data-likes]').textContent = num_likes
        manageLikeBtn(comment)
    })
}
let handleDislike = (event) => {
    let comment = event.target.closest('.comment')
    let id = comment.dataset.post || comment.dataset.thread
    let is_thread = comment.dataset.thread ? 'true': null
    let data = {
        id: id,
        is_thread: is_thread,
    }
    let url = '/forum/ajax/dislike/'
    ajax = post_fetch(url, data).then(res => res.json())
    ajax.then(res => {
        num_likes = res['num_likes']
        comment.querySelector('[data-likes]').textContent = num_likes
        manageLikeBtn(comment)
    })
}

function handleSubmit(event) {
    let comment = event.target.closest('.comment')
    console.log(comment)
    let parentId = comment.dataset.post
    if (!parentId) {
        parentId = comment.dataset.thread
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
    if (data['thread_parent']) {
        let thread_id = data['thread_parent']
        var comments = document.querySelector(`[data-thread="${thread_id}"]`)
    } else {
        let post_id = data['post']
        var comments = document.querySelector(`[data-post="${post_id}"]`)
    }
    // let comments = document.querySelector(`[data-post="${data.post}"]`)
    let thread = document.createElement('div')
    thread.dataset.thread = data['id']
    thread.classList.add('comment')
    let commentsMargin = window.getComputedStyle(comments).getPropertyValue('margin-left')
    let newMargin = parseInt(commentsMargin, 10) + 20
    thread.style.marginLeft = newMargin + 'px'

    let head = document.createElement('div')
    head.classList.add('head')

    for (let attr of ['author', 'likes', 'date']) {
        let elem = document.createElement('span')
        elem.textContent = data[attr]
        if (attr === 'likes') {elem.dataset.likes = 'likes'}
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

    let respondBtn = document.createElement('button')
    respondBtn.classList.add('respondBtn', 'myBtn')
    respondBtn.textContent = 'Odpowiedź'
    respondBtn.addEventListener('click', handleRespond)

    let dislikeBtn = document.createElement('button')
    dislikeBtn.classList.add('right', 'dislikeBtn', 'myBtn')
    dislikeBtn.textContent = 'Nie lubię'
    dislikeBtn.addEventListener('click', handleDislike)

    let likeBtn = document.createElement('button')
    likeBtn.classList.add('right', 'likeBtn', 'myBtn')
    likeBtn.textContent = 'Lubię'
    likeBtn.addEventListener('click', handleLike)

    commentBtns.append(respondBtn)
    commentBtns.append(dislikeBtn)
    commentBtns.append(likeBtn)
    thread.append(commentBtns)

    let showMoreBtn = document.createElement('button')
    showMoreBtn.classList.add('show-more')
    showMoreBtn.textContent = data['children_count'] + ' odpowiedzi. Naciśnij by zobaczyć więcej.'
    showMoreBtn.addEventListener('click', getThreads)
    thread.append(showMoreBtn)

    comments.after(thread)

}

let respondBtns = document.querySelectorAll('.respondBtn')
let likeBtns = document.querySelectorAll('.likeBtn')
let dislikeBtns = document.querySelectorAll('.dislikeBtn')
let moreThreads = document.querySelectorAll('.show-more')
for (let i=0; i < respondBtns.length; i++) {
    respondBtns[i].addEventListener('click', handleRespond)
    likeBtns[i].addEventListener('click', handleLike)
    dislikeBtns[i].addEventListener('click', handleDislike)
}
for (let i=0; i < moreThreads.length; i++) {
    moreThreads[i].addEventListener('click', getThreads)
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