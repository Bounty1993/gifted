supportBtn = document.getElementById('supportBtn')
supportBtn.onclick = () => {
  supportForm = document.getElementById('supportForm')
  supportForm.classList.toggle('hidden')
}
submitSupport = document.getElementById('submitSupport')
submitSupport.onclick = () => {
  amount = document.getElementById('amount')
  comment = document.getElementById('comment')
  data = {
    amount: amount.value,
    comment: comment.value
  }
  console.log(data)
}