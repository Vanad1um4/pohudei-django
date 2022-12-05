const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
const divMainTable = document.querySelector('#main-table')
const floatSearch = document.querySelector('#float-dimming-search')
const addBtn = document.querySelector('#add-food')
const closeBtn = document.querySelector('#float-cancel')
const inputSearchField = document.querySelector('#float-input')
const resCont = document.querySelector('#float-results-cont')
const floatyAddNew = document.querySelector('#floaty-add-new')
const floatyAddInput = document.querySelector('#floaty-add-input')
const floatyAddInfo = document.querySelector('#floaty-add-info')

const data = JSON.parse(document.getElementById('data').textContent)
// console.log(data)
let foodDict = {}

onLoad()

function onLoad() {
    initConstr(data)
    // addBtn.addEventListener("click", function clicked(event) { clickAddBtn(event) });
    addBtn.addEventListener("click", function clicked(event) {
        floatSearch.style.display = 'block'
        inputSearchField.focus()
    });
    // closeBtn.addEventListener("click", function clicked(event) { clickCloseBtn(event) });
    closeBtn.addEventListener("click", function clicked(event) { floatSearch.style.display = 'none' });
    inputSearchField.addEventListener("input", function clicked(event) { changeInput(event.target) });
    foodArrayConsrtuct(data[2])
    // console.log(foodDict)
}

function foodArrayConsrtuct(rawFood) {
    for (let i = 0; i < rawFood.length; i++) {
        // console.log(rawFood[i])
        foodDict[rawFood[i][0]] = rawFood[i][1]
    }
}

function changeInput(target) {
    // const queryArray = target.value.toLowerCase().split(' ').filter(val => val.length > 0)
    const queryArray = target.value.toLowerCase().split(' ').filter(val => val.length > 0)
    // console.log(target.value)
    // console.log(target.value.toLowerCase())

    let tempFoodDict = {}
    for (let i in foodDict) {
        if (queryArray.every(word => foodDict[i].toLowerCase().includes(word))){
            tempFoodDict[i] = foodDict[i]
        }
    }
    // console.log(tempFoodDict)

    resultsConstruct(resCont, tempFoodDict)

    function resultsConstruct(container, selectedFood) {
        while (container.firstChild) {
            container.firstChild.remove()
        }

        for (let i in tempFoodDict) {
            // console.log(i)
            // console.log(tempFoodDict[i])
            const resDiv = document.createElement('DIV')
            resDiv.classList.add('float-results-line')
            resDiv.setAttribute('id', 'food' + i)
            resDiv.textContent = `${tempFoodDict[i]}`
            container.appendChild(resDiv)

            resDiv.addEventListener("click", function clicked(event) { foodResultClicked(event.target, tempFoodDict) });
        }
    }
}

function foodResultClicked(target, tempFoodDict) {
    console.log(target.innerText)
    let foodId = parseInt(target.getAttribute('id').replace('food', ''))
    floatSearch.style.display = 'none'

    const floatyAddName = document.querySelector('#floaty-add-name')
    const floatyAddYes = document.querySelector('#floaty-add-yes')
    const floatyAddNo = document.querySelector('#floaty-add-no')

    floatyAddName.innerText = target.innerText
    floatyAddInfo.innerText = 'Введите вес блюда:'

    floatyAddYes.addEventListener("click", function clicked() {
        floatyAddYesPressed(foodId)
    })
    floatyAddNo.addEventListener("click", function clicked() {
        floatyAddNew.style.display = 'none'
        floatSearch.style.display = 'block'
        inputSearchField.focus()
    })
    floatyAddInput.value = ''

    floatyAddNew.style.display = 'block'

    floatyAddInput.focus()
    // console.log(foodId)
    console.log(data, foodId)
}

function floatyAddYesPressed(foodId) {
    const newWeight = floatyAddInput.value
    console.log(newWeight)
    // console.log(/^\d+$/.test(newWeight))
    if (newWeight === '') {
        floatyAddInfo.innerText = 'Вы не ввели вес!'
    } else if (!(/^\d+$/.test(newWeight))) {
        floatyAddInfo.innerText = 'Введите только цифры, граммы, целое цисло!'
    }
    else {
        console.log('lol, ok')

    fetch(`/add_food_to_diary/`,
    {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'food_id': foodId, 'food_weight': newWeight})
    })
        .then(response => response.json())
        .then(result => {
            console.log(result)
            if (result['result'] == 'success') {
                console.log('lol, reset')
                window.location.reload();
            }
        })
    }
}

function initConstr(data) {
    const todaysFood = data[0]
    const todaysKcals = data[1]

    const norn_val = document.querySelector('.norm-val')
    norn_val.textContent = todaysKcals

    // const divMainTable = document.querySelector('#main-table')
    const divTableHead = document.createElement('DIV')
    const divNum = document.createElement('DIV')
    const divName = document.createElement('DIV')
    const divWeight = document.createElement('DIV')
    const divKcals = document.createElement('DIV')
    const divPerc = document.createElement('DIV')
    divTableHead.classList.add('row')
    divNum.classList.add('cell', 'cell-head')
    divName.classList.add('cell', 'cell-head')
    divWeight.classList.add('cell', 'cell-head')
    divKcals.classList.add('cell', 'cell-head')
    divPerc.classList.add('cell', 'cell-head')
    divNum.textContent = '№'
    divName.textContent = 'Блюдо'
    divWeight.textContent = 'Вес'
    divKcals.textContent = 'Ккал'
    divPerc.textContent = '%'
    divTableHead.appendChild(divNum)
    divTableHead.appendChild(divName)
    divTableHead.appendChild(divWeight)
    divTableHead.appendChild(divKcals)
    divTableHead.appendChild(divPerc)
    divMainTable.appendChild(divTableHead)

    let sumKcals = 0
    for (let i = 0; i < todaysFood.length; i++) {
        sumKcals += todaysFood[i][2]
        addRow(i+1, todaysFood[i][0], todaysFood[i][1], todaysFood[i][2], todaysKcals)
    }
    const curr_val_kcals = document.querySelector('.curr-kcals')
    const curr_val_perc = document.querySelector('.curr-perc')
    curr_val_kcals.textContent = sumKcals
    curr_val_perc.textContent = Math.round(sumKcals / todaysKcals * 100)
}

function addRow(i, name, weight, kcals, todaysKcals) {
    const divTableRow = document.createElement('DIV')
    const divNum = document.createElement('DIV')
    const divName = document.createElement('DIV')
    const divWeight = document.createElement('DIV')
    const divKcals = document.createElement('DIV')
    const divPerc = document.createElement('DIV')
    divTableRow.classList.add('row')
    divNum.classList.add('cell', 'cell-num')
    divName.classList.add('cell', 'cell-name')
    divWeight.classList.add('cell', 'cell-w')
    divKcals.classList.add('cell', 'cell-k')
    divPerc.classList.add('cell', 'cell-p')
    divNum.textContent = `${i}`
    divName.textContent = `${name}`
    divWeight.textContent = `${weight}`
    divKcals.textContent = `${kcals}`
    divPerc.textContent = `${Math.round(kcals / todaysKcals * 100)}`
    divTableRow.appendChild(divNum)
    divTableRow.appendChild(divName)
    divTableRow.appendChild(divWeight)
    divTableRow.appendChild(divKcals)
    divTableRow.appendChild(divPerc)
    divMainTable.appendChild(divTableRow)
}
