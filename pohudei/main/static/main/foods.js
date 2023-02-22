const divMainTable = document.querySelector('#main-table')

const addBtn = document.querySelector('#add-food')

const floatyAddNew = document.querySelector('.floaty-add-new')
const floatyAddName = document.querySelector('.floaty-add-name-textarea')
const floatyAddKcals = document.querySelector('.floaty-add-kcals-input')
const floatyAddNameWarn = document.querySelector('.floaty-add-name-warn')
const floatyAddKcalsWarn = document.querySelector('.floaty-add-kcals-warn')
const floatyAddYes = document.querySelector('.floaty-add-yes')
const floatyAddNo = document.querySelector('.floaty-add-no')

const floatyEdit = document.querySelector('.floaty-edit')
const floatyEditName = document.querySelector('.floaty-edit-name-textarea')
const floatyEditKcals = document.querySelector('.floaty-edit-kcals-input')
const floatyEditNameWarn = document.querySelector('.floaty-edit-name-warn')
const floatyEditKcalsWarn = document.querySelector('.floaty-edit-kcals-warn')
const floatyEditUpdate = document.querySelector('.floaty-edit-update-btn')
const floatyEditDelete = document.querySelector('.floaty-edit-delete-btn')
const floatyEditYesDelete = document.querySelector('.floaty-edit-yes-delete-btn')
const floatyEditCancel = document.querySelector('.floaty-edit-cancel-btn')

const floatyInfoDiv = document.querySelector('.floaty-info')
const floatyInfoText = document.querySelector('.floaty-info-header')

const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
const data = JSON.parse(document.getElementById('data').textContent)
console.log(data)
const foods = data['foods']
let selectedFood = 0
const waitMsFast = 1000
const waitMsSlow = 2000


onLoad()

function onLoad() {
    mainTableOfFoodsConstruct()

    addBtn.addEventListener("click", () => {
        floatyAddNew.style.display = 'block'
    });

    floatyAddYes.addEventListener("click", () => {
        clickedNewFoodBtn()
    })

    floatyAddNo.addEventListener("click", () => {
        floatyAddNew.style.display = 'none'
    })

    floatyEditUpdate.addEventListener("click", () => {
        clickedUpdateFoodBtn()
    })

    floatyEditDelete.addEventListener("click", () => {
        floatyEditYesDelete.style.display = 'block'
    })

    floatyEditYesDelete.addEventListener("click", () => {
        clickedDeleteFoodBtn()
    })

    floatyEditCancel.addEventListener("click", () => {
        floatyEditYesDelete.style.display = 'none'
        floatyEdit.style.display = 'none'
    })
}


async function clickedEditFoodBtn(target) {
    selectedFood = parseInt(target.parentNode.getAttribute('id').replace('catalogue', ''))
    floatyEdit.style.display = 'block'
    let foodName = ''
    let foodKcals = 0
    for (let i=0; i<foods.length; i++) {
        if (foods[i][0] === selectedFood) {
            foodName = foods[i][1]
            foodKcals = foods[i][2]
            break
        }
    }
    floatyEditName.value = foodName
    floatyEditKcals.value = foodKcals
}


async function clickedUpdateFoodBtn() {
    const foodName = floatyEditName.value
    const foodKcals = parseInt(floatyEditKcals.value)
    floatyEditNameWarn.style.display = 'none'
    floatyEditKcalsWarn.style.display = 'none'
    if (foodName == '') {
        floatyEditNameWarn.style.display = 'block'
    } else if (!(isNumeric(foodKcals))) {
        floatyEditKcalsWarn.style.display = 'block'
    } else {
        floatyEdit.style.display = 'none'
        floatyInfoDiv.style.display = 'block'
        floatyInfoText.textContent = 'Ждите...'
        floatyInfoText.style.color = 'white'
        fetch(`/update_food_in_catalogue/`,
        {
            method: 'PUT',
            headers: {
                'X-CSRFToken': csrftoken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'food_id': selectedFood, 'food_name': foodName, 'food_kcals': foodKcals})
        })
        .then(response => {
            if (response.status === 204) {
                floatyInfoText.textContent = 'Успешно!'
                floatyInfoText.style.color = 'LawnGreen'
            } else if (response.status === 409) {
                floatyInfoText.textContent = 'Блюдо с таким названием уже есть...'
                floatyInfoText.style.color = 'orange'
            } else {
                floatyInfoText.textContent = 'Произошло что-то непонятное, походу все сломалось...'
                floatyInfoText.style.color = 'red'
            }
        })
        .then(await sleep(waitMsFast))
        .then(() => { window.location.reload() })
    }
}


async function clickedDeleteFoodBtn() {
    floatyEdit.style.display = 'none'
    floatyInfoDiv.style.display = 'block'
    floatyInfoText.textContent = 'Ждите...'
    floatyInfoText.style.color = 'white'
    fetch(`/delete_food_from_catalogue/`,
    {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrftoken,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'food_id': selectedFood})
    })
    .then(response => {
        if (response.status === 204) {
            floatyInfoText.textContent = 'Успешно!'
            floatyInfoText.style.color = 'LawnGreen'
        } else if (response.status === 409) {
            floatyInfoText.textContent = 'Уже используется, удалить невозможно.'
            floatyInfoText.style.color = 'orange'
        } else {
            floatyInfoText.textContent = 'Произошло что-то непонятное, походу все сломалось...'
            floatyInfoText.style.color = 'red'
        }
    })
    .then(await sleep(waitMsFast))
    .then(() => { window.location.reload() })

}


async function clickedNewFoodBtn() {
    const newFoodName = floatyAddName.value
    const newFoodKcals = parseInt(floatyAddKcals.value)
    floatyAddNameWarn.style.display = 'none'
    floatyAddKcalsWarn.style.display = 'none'

    if (newFoodName == '') {
        floatyAddNameWarn.style.display = 'block'
    } else if (!(isNumeric(newFoodKcals))) {
        floatyAddKcalsWarn.style.display = 'block'
    } else {
        floatyAddNew.style.display = 'none'
        floatyInfoDiv.style.display = 'block'
        floatyInfoText.textContent = 'Ждите...'
        floatyInfoText.style.color = 'white'
        fetch(`/add_food_to_catalogue/`,
        {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'food_name': newFoodName, 'food_kcals': newFoodKcals})
        })
        .then(response => {
            if (response.status === 204) {
                floatyInfoText.textContent = 'Успешно!'
                floatyInfoText.style.color = 'LawnGreen'
            } else if (response.status === 409) {
                floatyInfoText.textContent = 'Блюдо с таким названием уже есть...'
                floatyInfoText.style.color = 'orange'
            } else {
                floatyInfoText.textContent = 'Произошло что-то непонятное, походу все сломалось...'
                floatyInfoText.style.color = 'red'
            }
        })
        .then(await sleep(waitMsFast))
        .then(window.location.reload())
    }
}

function mainTableOfFoodsConstruct() {
    const divTableHead = document.createElement('DIV')
    const divName = document.createElement('DIV')
    const divKcals = document.createElement('DIV')
    divTableHead.classList.add('row')
    divName.classList.add('cell', 'cell-head', 'cell-name')
    divKcals.classList.add('cell', 'cell-head')
    divName.textContent = 'Блюдо'
    divKcals.textContent = 'Ккал/100г'
    divTableHead.appendChild(divName)
    divTableHead.appendChild(divKcals)
    divMainTable.appendChild(divTableHead)

    for (let i = 0; i < foods.length; i++) {
        addRow(foods[i][0], foods[i][1], foods[i][2])
    }
}


function addRow(id, name, kcals) {
    const divTableRow = document.createElement('DIV')
    const divName = document.createElement('DIV')
    const divKcals = document.createElement('DIV')
    divTableRow.classList.add('row')
    divTableRow.setAttribute('id', 'catalogue' + id)
    divName.classList.add('cell', 'cell-name')
    divKcals.classList.add('cell', 'cell-k')
    divName.textContent = `${name}`
    divKcals.textContent = `${kcals}`
    divTableRow.appendChild(divName)
    divTableRow.appendChild(divKcals)
    divMainTable.appendChild(divTableRow)

    divTableRow.addEventListener("click", (event) => { clickedEditFoodBtn(event.target) });
}

function sleep(ms) {return new Promise(resolve => setTimeout(resolve, ms));}

const isNumeric = (num) => (typeof(num) === 'number' || typeof(num) === "string" && num.trim() !== '') && !isNaN(num);
