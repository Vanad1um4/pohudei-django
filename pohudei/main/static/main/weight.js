// TODO: refactor this slightly maybe?

const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
const divMainTable = document.querySelector('.main-table')
const weightData = JSON.parse(document.getElementById('data').textContent)
console.log(weightData)
let selectedWeightId = 0
const waitMs = 1000

onLoad()
async function onLoad() {
    initTableConstruct(weightData)

    document.querySelector('.add-weight-btn').addEventListener("click", (event) => { clickedAddBtn(event) });

    document.querySelector('.floaty-add-send-btn').addEventListener("click", (event) => { clickedFloatyAddSendBtn(event) });
    document.querySelector('.floaty-add-cancel-btn').addEventListener("click", () => { clickedFloatyAddCancelBtn() });

    document.querySelector('.floaty-edit-update').addEventListener("click", () => { clickedFloatyEditUpdateBtn() });
    document.querySelector('.floaty-edit-delete').addEventListener("click", () => { clickedFloatyEditDeleteBtn() });
    document.querySelector('.floaty-edit-delete-yes').addEventListener("click", () => { clickedFloatyEditDeleteYesBtn() });
    document.querySelector('.floaty-edit-cancel').addEventListener("click", () => { clickedFloatyEditCancelBtn() });
}

function clickedWeight(target) {
    selectedWeightId = parseInt(target.parentElement.getAttribute('id').replace('weight', ''))
    document.querySelector('.floaty-edit').style.display = 'block'
    const dateStr = target.parentElement.childNodes[0].textContent
    // const dateDate = new Date(dateStr)
    const weight = target.parentElement.childNodes[1].textContent
    // document.querySelector('.edit-header').textContent = `Редактируем вес от ${dateDate.toLocaleString('ru', {month: 'long', day: 'numeric'})}.`
    document.querySelector('.edit-header').textContent = `Редактируем вес от ${dateStr}.`
    document.querySelector('.edit-input').value = weight
    document.querySelector('.edit-input').focus()
}


async function clickedFloatyEditUpdateBtn() {
    const messageDiv = document.querySelector('.floaty-info-message')
    const weightValue = document.querySelector('.floaty-edit-input').value
    if (!(numTest(weightValue))) {
        document.querySelector('.floaty-edit-warn').style.display = 'block'
    } else {
        document.querySelector('.floaty-edit-warn').style.display = 'none'
        document.querySelector('.floaty-edit').style.display = 'none'
        document.querySelector('.floaty-info').style.display = 'block'
        messageDiv.textContent = 'Ждите...'

        fetch(`/update_weight/`,
        {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'weight_id': selectedWeightId, 'weight': weightValue})
        })
            .then(response => response.json())
            .then(result => {
                if (result['result'] === 'success') {
                    messageDiv.textContent = 'Успешно...'
                } else if (result['result'] === 'failure') {
                    messageDiv.textContent = 'Произошло что-то непонятное, походу все сломалось...'
                }
            })
            .then(await sleep(waitMs))
            .then(() => { window.location.reload() })

    }
}

function clickedFloatyEditDeleteBtn() {
    document.querySelector('.floaty-edit-delete-yes').style.display = 'block'
}

async function clickedFloatyEditDeleteYesBtn() {
    const messageDiv = document.querySelector('.floaty-info-message')
    document.querySelector('.floaty-edit-warn').style.display = 'none'
    document.querySelector('.floaty-edit').style.display = 'none'
    document.querySelector('.floaty-info').style.display = 'block'
    messageDiv.textContent = 'Ждите...'

    fetch(`/delete_weight/`,
    {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'weight_id': selectedWeightId})
    })
        .then(response => response.json())
        .then(result => {
            if (result['result'] === 'success') {
                messageDiv.textContent = 'Успешно...'
            } else if (result['result'] === 'failure') {
                messageDiv.textContent = 'Произошло что-то непонятное, походу все сломалось...'
            }
        })
        .then(await sleep(waitMs))
        .then(() => { window.location.reload() })
}


function clickedFloatyEditCancelBtn() {
    document.querySelector('.floaty-edit').style.display = 'none'
}






function clickedAddBtn(event) {
    document.querySelector('.floaty-add').style.display = 'block'
    const todayStr = new Date(Date.now()).toISOString().split('T')[0]
    // console.log(new Date(Date.now()).toISOString())
    document.querySelector('.input-date').value = todayStr
    document.querySelector('.floaty-add-input').focus()
}

async function clickedFloatyAddSendBtn(event) {
    const messageDiv = document.querySelector('.floaty-info-message')
    const dateValue = document.querySelector('.input-date').value
    const weightValue = document.querySelector('.floaty-add-input').value
    if (!(numTest(weightValue))) {
        document.querySelector('.div-weight-warn').style.display = 'block'
    } else {
        document.querySelector('.div-weight-warn').style.display = 'none'
        document.querySelector('.floaty-add').style.display = 'none'
        document.querySelector('.floaty-info').style.display = 'block'
        messageDiv.textContent = 'Ждите...'

        fetch(`/add_new_weight/`,
        {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'date': dateValue, 'weight': weightValue})
        })
            .then(response => response.json())
            .then(result => {
                if (result['result'] === 'success') {
                    messageDiv.textContent = 'Успешно...'
                } else if (result['result'] === 'duplication') {
                    messageDiv.textContent = 'Запись за этот день уже есть...'
                } else if (result['result'] === 'failure') {
                    messageDiv.textContent = 'Произошло что-то непонятное, походу все сломалось...'
                }
            })
            .then(await sleep(waitMs))
            .then(() => { window.location.reload() })
    }
}

function clickedFloatyAddCancelBtn() {
    document.querySelector('.floaty-add').style.display = 'none'
}

function initTableConstruct(weightsData) {
    const divTableHead = document.createElement('DIV')
    const divDate = document.createElement('DIV')
    const divWeight = document.createElement('DIV')
    divTableHead.classList.add('row')
    divDate.classList.add('cell', 'cell-head')
    divWeight.classList.add('cell', 'cell-head')
    divDate.textContent = 'Дата'
    divWeight.textContent = 'Вес'
    divTableHead.appendChild(divDate)
    divTableHead.appendChild(divWeight)
    divMainTable.appendChild(divTableHead)

    for (let i = 0; i < weightsData.length; i++) {
        addRow(weightsData[i][0], weightsData[i][1], weightsData[i][2])
    }
}
function addRow(id, date, weight) {
    const divTableRow = document.createElement('DIV')
    divTableRow.setAttribute('id', 'weight' + id)
    const divDate = document.createElement('DIV')
    const divWeight = document.createElement('DIV')
    divTableRow.classList.add('row')
    divDate.classList.add('cell', 'cell-date')
    divWeight.classList.add('cell', 'cell-weight')
    const dateFromString = new Date(date)
    const humanDateString = dateFromString.toLocaleString('ru', {month: 'long', day: 'numeric'})
    divDate.textContent = `${humanDateString}`
    divWeight.textContent = `${weight}`
    divTableRow.appendChild(divDate)
    divTableRow.appendChild(divWeight)
    divMainTable.appendChild(divTableRow)

    divTableRow.addEventListener("click", (event) => { clickedWeight(event.target) });
}

// const isNumeric = (num) => (typeof(num) === 'number' || typeof(num) === "string" && num.trim() !== '') && !isNaN(num);

function numTest(num) {
    // const regex = new RegExp(/\b[\d]{2}[.][\d]{1}\b/)
    const regex = new RegExp(/^\b[\d]{2,3}[.][\d]{1}\b$|^\b[\d]{2,3}\b$/gm)
    return regex.test(num)
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
