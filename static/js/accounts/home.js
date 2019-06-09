$('.deleteBtn').on('click', function() {
    message_id = this.name
    data = {id: message_id}
    url = `/rooms/ajax/message/delete/`
    ajax = post_fetch(url, data).then(response => response.json())
    ajax.then(response => {
        if (response['is_valid'] === 'true') {
            this.closest('li').remove()
        } else {
            alert('Wystąpił błąd' + response['error'])
        }
    })
})
