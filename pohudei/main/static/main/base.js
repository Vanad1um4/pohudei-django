const input = document.querySelector('#test-input')
input.addEventListener("input", function clicked(event) { console.log(event.target.value) });
console.log(input.value)
