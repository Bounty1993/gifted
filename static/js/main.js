function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function post_fetch(url, data) {
  // let guest = document.getElementById("guest_input")
  // let data = {guest: guest.value, type: type}
  // let url = '/rooms/1/guests/'
  return fetch(url, {
    method: "post",
    credentials: "include",
    headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  })
};

function makeMessage(type, message) {
    msg = document.createElement('div')
    msg.classList.add('alert', `alert-${type}`, 'alert-dismissible')
    msg.role = 'alert'
    msg.textContent = message
    return msg
};