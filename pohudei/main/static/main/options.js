const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
const optionsData = JSON.parse(document.getElementById('data').textContent)
console.log(optionsData)
const waitMs = 1000

onInit()

function onInit() {
    document.querySelector('.weights-pull-num').value = optionsData['weights_to_pull']
    document.querySelector('.weights-pull-num').addEventListener('input', () => { saveWeightsPullNum() });
}

async function saveWeightsPullNum() {
    const lastVal = document.querySelector('.weights-pull-num').value
    await sleep(waitMs)
    const newVal = document.querySelector('.weights-pull-num').value
    if (lastVal === newVal) {
        document.querySelector('.weights-pull-num').disabled = true
        document.querySelector('.weights-pull-num').style.background = 'grey'

        fetch(`/set_weights_to_pull/`,
        {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'weights_to_pull': newVal})
        })
            .then(response => response.json())
            .then(result => {
                if (result['result'] === 'success') {
                    console.log('success')
                    document.querySelector('.weights-pull-num').disabled = false
                    document.querySelector('.weights-pull-num').style.background = 'green'
                } else if (result['result'] === 'failure') {
                    console.log('failure')
                    document.querySelector('.weights-pull-num').disabled = false
                    document.querySelector('.weights-pull-num').style.background = 'red'
                }
            })
            .then(await sleep(waitMs))
            .then(() => { document.querySelector('.weights-pull-num').style.background = 'transparent' })
    }
}


async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// TEST

// const textarea = document.querySelector('.textarea')
// const button = document.querySelector('.button')
// button.addEventListener('click', () => { sendText() });
//
// function sendText() {
//     const text = textarea.value
//     fetch(`/test/`,
//     {
//         method: 'POST',
//         headers: {
//             'X-CSRFToken': csrftoken,
//             'Accept': 'application/json',
//             'Content-Type': 'application/json'
//         },
//         // body: JSON.stringify({'text': text})
//         body: JSON.stringify({'food': text})
//     })
//     .then(response => response.json())
//     .then(result => {
//         console.log(result)
//     })
// }










