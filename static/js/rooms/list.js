trendy_panel = document.getElementById('trendy-panel')

trendy_panel.onclick = () => {
    most_trendy = document.getElementById('most-trendy')
    most_trendy.classList.toggle('hidden')
}

function observerSubmit(event) {
    let room_id = event.target.name
    url = `${room_id}/ajax/observers/`
    console.log(url)
    ajax = post_fetch(url, {}).then(response => response.json())
    ajax.then(response => {
        if (response['is_valid']==='true') {
            event.target.textContent = 'Dodano do obserwowanych'
            event.target.removeEventListener('click', observerSubmit)
        } else {
            alert('Źle')
        }
    })
}

observerBtn = document.querySelectorAll('.observerBtn')

for (let Btn of observerBtn) {
    Btn.addEventListener('click', observerSubmit)
}