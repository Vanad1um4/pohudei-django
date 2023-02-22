const heightInput = document.querySelector('.height-num')
const useCoeffsInput = document.querySelector('.use-coeffs-tick')

console.log(useCoeffsInput)

const saveBtn = document.querySelector('.save')


const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
const optionsData = JSON.parse(document.getElementById('data').textContent)
console.log(optionsData)
const waitMs = 1000

onInit()


function onInit() {
    heightInput.value = optionsData['height']
    if (optionsData['use_coeffs']) {
        useCoeffsInput.setAttribute('checked', 'checked')
    }
    saveBtn.addEventListener('click', () => { saveTest() });
}


async function saveTest() {
    const heightVal = parseInt(heightInput.value)
    const useCoeffsVal = useCoeffsInput.checked
    if (Number.isInteger(heightVal)) {
        heightInput.disabled = true
        heightInput.style.background = 'lightgrey'
        useCoeffsInput.disabled = true
        saveBtn.classList.remove('active', 'inactive', 'success', 'fail')
        saveBtn.classList.add('inactive')

        fetch(`/set_options/`,
        {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'height': heightVal, 'use_coeffs': useCoeffsVal})
        })
        .then(response => {
            if (response.status === 204) {
                heightInput.disabled = false
                useCoeffsInput.disabled = false
                heightInput.style.background = 'transparent'
                saveBtn.classList.remove('active', 'inactive', 'success', 'fail')
                saveBtn.classList.add('success')
            } else {
                heightInput.disabled = false
                saveBtn.classList.remove('active', 'inactive', 'success', 'fail')
                saveBtn.classList.add('fail')
            }
        })
        .then(await sleep(waitMs))
        .then(() => {
            heightInput.style.background = 'transparent'
            saveBtn.classList.remove('active', 'inactive', 'success', 'fail')
            saveBtn.classList.add('active')
        })
    }
}


async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
