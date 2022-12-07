const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
const divMainTable = document.querySelector('.main-table')
const weightData = JSON.parse(document.getElementById('data').textContent)
let selectedWeightId = 0
// console.log(weightData)
// console.log(weightData.length)

onLoad()
function onLoad() {
    initPrep(weightData)

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
    // console.log(target.parentElement.childNodes)
    const dateStr = target.parentElement.childNodes[0].textContent
    const dateDate = new Date(dateStr)
    // console.log(date.toLocaleString('ru', {month: 'long', day: 'numeric'}))
    const weight = target.parentElement.childNodes[1].textContent
    document.querySelector('.edit-header').textContent = `Редактируем вес от ${dateDate.toLocaleString('ru', {month: 'long', day: 'numeric'})}.`
    document.querySelector('.edit-input').value = weight
    document.querySelector('.edit-input').focus()
}


function clickedFloatyEditUpdateBtn() {
    const messageDiv = document.querySelector('.floaty-info-message')
    const weightValue = document.querySelector('.floaty-edit-input').value
    // console.log(numTest(weightValue))
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
                // console.log(result)
                if (result['result'] === 'success') {
                    messageDiv.textContent = 'Успешно...'
                    window.location.reload();
                } else if (result['result'] === 'failure') {
                    messageDiv.textContent = 'Произошло что-то непонятное, походу все сломалось...'
                    window.location.reload();
                }
            })

    }
}

function clickedFloatyEditDeleteBtn() {
    document.querySelector('.floaty-edit-delete-yes').style.display = 'block'
}

function clickedFloatyEditDeleteYesBtn() {
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
            // console.log(result)
            if (result['result'] === 'success') {
                messageDiv.textContent = 'Успешно...'
                window.location.reload();
            } else if (result['result'] === 'failure') {
                messageDiv.textContent = 'Произошло что-то непонятное, походу все сломалось...'
                window.location.reload();
            }
        })
}



function clickedFloatyEditCancelBtn() {
    document.querySelector('.floaty-edit').style.display = 'none'
}















function clickedAddBtn(event) {
    document.querySelector('.floaty-add').style.display = 'block'
    const todayStr = new Date(Date.now()).toISOString().split('T')[0]
    document.querySelector('.input-date').value = todayStr
    document.querySelector('.floaty-add-input').focus()
}

function clickedFloatyAddSendBtn(event) {
    const messageDiv = document.querySelector('.floaty-info-message')
    const dateValue = document.querySelector('.input-date').value
    const weightValue = document.querySelector('.floaty-add-input').value
    // console.log(numTest(weightValue))
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
                // console.log(result)
                if (result['result'] === 'success') {
                    messageDiv.textContent = 'Успешно...'
                    window.location.reload();
                } else if (result['result'] === 'duplication') {
                    messageDiv.textContent = 'Запись за этот день уже есть...'
                    window.location.reload();
                } else if (result['result'] === 'failure') {
                    messageDiv.textContent = 'Произошло что-то непонятное, походу все сломалось...'
                    window.location.reload();
                }
            })
    }
}

function clickedFloatyAddCancelBtn() {
    document.querySelector('.floaty-add').style.display = 'none'
}

function initPrep(weightsData) {
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
        // console.log(weightsData[i])
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
    divDate.textContent = `${date}`
    divWeight.textContent = `${weight}`
    divTableRow.appendChild(divDate)
    divTableRow.appendChild(divWeight)
    divMainTable.appendChild(divTableRow)

    divTableRow.addEventListener("click", (event) => { clickedWeight(event.target) });
}

// const isNumeric = (num) => (typeof(num) === 'number' || typeof(num) === "string" && num.trim() !== '') && !isNaN(num);

function numTest(num) {
    const regex = new RegExp(/\b[\d]{2}[.][\d]{1}\b/)
    return regex.test(num)
}
