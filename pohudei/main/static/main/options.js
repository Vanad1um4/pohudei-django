const heightInput = document.querySelector('.height-num')
const heightSaveBtn = document.querySelector('.height-save')


const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
const optionsData = JSON.parse(document.getElementById('data').textContent)
console.log(optionsData)
const waitMs = 1000

onInit()


function onInit() {
    heightInput.value = optionsData['height']
    heightSaveBtn.addEventListener('click', () => { saveWeight() });
}


async function saveWeight() {
    const height_val = parseInt(heightInput.value)
    console.log(height_val)
    console.log(Number.isInteger(height_val))
    if (Number.isInteger(height_val)) {
        heightInput.disabled = true
        heightInput.style.background = 'grey'

        fetch(`/set_height/`,
        {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'height': height_val})
        })
            .then(response => response.json())
            .then(result => {
                if (result['result'] === 'success') {
                    console.log('success')
                    heightInput.disabled = false
                    heightInput.style.background = 'green'
                } else if (result['result'] === 'failure') {
                    console.log('failure')
                    heightInput.disabled = false
                    heightInput.style.background = 'red'
                }
            })
            .then(await sleep(waitMs))
            .then(() => { heightInput.style.background = 'transparent' })
    }
}


async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
