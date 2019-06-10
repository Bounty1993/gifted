let respondBtns = document.querySelectorAll('.respondBtn')

function handleRespond(event) {
    let comment = event.target.closest('.comment')
    let form = document.createElement('div')
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
    sendBtn.classList.add('forumBtn', 'mainBtn')
    sendBtn.textContent = 'Wyślij odpowiedź'
    sendBtn.addEventListener('click', handleSubmit)
    form.append(subjectInput, contentInput, sendBtn)
    comment.after(form)

}

function handleSubmit(event) {
    let comment = event.target.closest('.comment')
    let subject = comment.children[0].value
    let content = comment.children[1].value
    data = {subject: subject, content:content}
    url = `/forum/1/ajax/thread/create/`
    ajax = post_fetch(url, data).then(response => response.json())
    ajax.then(response => {
        console.log(response)
    })
}

for (let i=0; i < respondBtns.length; i++) {
    respondBtns[i].addEventListener('click', handleRespond)
}