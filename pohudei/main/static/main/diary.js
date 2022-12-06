const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

const divMainTable = document.querySelector('#main-table')
const currValKcalsDiv = document.querySelector('.curr-kcals')
let currValKcals = 0
const currValPercDiv = document.querySelector('.curr-perc')
// let foodNum = 1

const floatSearch = document.querySelector('#float-dimming-search')
const addBtn = document.querySelector('#add-food')
const closeBtn = document.querySelector('#float-cancel')
const inputSearchField = document.querySelector('#float-input')
const resCont = document.querySelector('#float-results-cont')
const floatyAddNew = document.querySelector('#floaty-add-new')
const floatyAddInput = document.querySelector('#floaty-add-input')
const floatyAddInfo = document.querySelector('#floaty-add-info')
const floatyInfoDiv = document.querySelector('#floaty-info-div')
const floatyInfoText = document.querySelector('#floaty-info-text')

const floatyEditMainDiv = document.querySelector('#floaty-edit')
const floatyEditFoodName = document.querySelector('#name-food')
const floatyEditWeight1 = document.querySelector('#edit-weight-input-curr')
const floatyEditupdateBtn = document.querySelector('#update-btn')
const floatyEditdeleteBtn = document.querySelector('#delete-btn')
const floatyEdityesDeleteBtn = document.querySelector('#yes-delete-btn')
const floatyEditcancelBtn = document.querySelector('#edit-cancel-btn')

const data = JSON.parse(document.getElementById('data').textContent)
const todaysFood = data[0]
const todaysNormKcals = data[1]
let todaysEatenKcals = 0
console.log(data)
let foodDict = {}

onLoad()

function onLoad() {
    initPrep(data)
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

async function floatyAddYesPressed(foodId) {
    const newWeight = parseInt(floatyAddInput.value)
    // console.log(/^\d+$/.test(newWeight))
    // console.log(newWeight)
    if (newWeight === '') {
        floatyAddInfo.innerText = 'Вы не ввели вес!'
    } else if (!(/^\d+$/.test(newWeight))) {
        floatyAddInfo.innerText = 'Введите только цифры, граммы, целое цисло!'
    }
    else {
        // console.log('lol, ok')
        floatyAddNew.style.display = 'none'
        floatyInfoDiv.style.display = 'block'
        floatyInfoText.innerText = 'Ждите...'

        // await sleep(1000)
        // floatyInfoDiv.style.display = 'none'
        //////////////////////
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
                    // console.log('lol, pacan k uspehu prishel xD')
                    window.location.reload();
                } else if (result['result'] == 'failure') {
                    // console.log('lol, servak zafeililsya xD')
                    floatyInfoText.innerText = 'Произошло что-то непонятное, походу все сломалось...'
                    window.location.reload();
                }
            })
    }
}

function initPrep() {
    const normVal = document.querySelector('.norm-val')
    normVal.textContent = todaysNormKcals

    const divTableHead = document.createElement('DIV')
    // const divNum = document.createElement('DIV')
    const divName = document.createElement('DIV')
    const divWeight = document.createElement('DIV')
    const divKcals = document.createElement('DIV')
    const divPerc = document.createElement('DIV')
    divTableHead.classList.add('row')
    // divNum.classList.add('cell', 'cell-head')
    divName.classList.add('cell', 'cell-head')
    divWeight.classList.add('cell', 'cell-head')
    divKcals.classList.add('cell', 'cell-head')
    divPerc.classList.add('cell', 'cell-head')
    // divNum.textContent = '№'
    divName.textContent = 'Блюдо'
    divWeight.textContent = 'Вес'
    divKcals.textContent = 'Ккал'
    divPerc.textContent = '%'
    // divTableHead.appendChild(divNum)
    divTableHead.appendChild(divName)
    divTableHead.appendChild(divWeight)
    divTableHead.appendChild(divKcals)
    divTableHead.appendChild(divPerc)
    divMainTable.appendChild(divTableHead)

    currValKcalsDiv.textContent = 0
    currValPercDiv.textContent = 0

    for (let i = 0; i < todaysFood.length; i++) {
        // addRow(i+1, todaysFood[i][0], todaysFood[i][1], todaysFood[i][2], todaysNormKcals)
        addRow(todaysFood[i][0], todaysFood[i][1], todaysFood[i][2], todaysFood[i][3], todaysNormKcals)
    }
}


// function addRow(i, name, weight, kcals, todaysNormKcals) {
function addRow(id, name, weight, kcals, todaysNormKcals) {
    const divTableRow = document.createElement('DIV')
    // const divNum = document.createElement('DIV')
    const divName = document.createElement('DIV')
    const divWeight = document.createElement('DIV')
    const divKcals = document.createElement('DIV')
    const divPerc = document.createElement('DIV')
    divTableRow.classList.add('row')
    divTableRow.setAttribute('id', 'diary' + id)
    // divNum.classList.add('cell', 'cell-num')
    divName.classList.add('cell', 'cell-name')
    divWeight.classList.add('cell', 'cell-w')
    divKcals.classList.add('cell', 'cell-k')
    divPerc.classList.add('cell', 'cell-p')
    // divNum.textContent = `${i}`
    divName.textContent = `${name}`
    divWeight.textContent = `${weight}`
    divKcals.textContent = `${kcals}`
    divPerc.textContent = `${Math.round(kcals / todaysNormKcals * 100)}`
    // divTableRow.appendChild(divNum)
    divTableRow.appendChild(divName)
    divTableRow.appendChild(divWeight)
    divTableRow.appendChild(divKcals)
    divTableRow.appendChild(divPerc)
    divMainTable.appendChild(divTableRow)

    divTableRow.addEventListener("click", (event) => { clickedDiary(event.target) });

    currValKcals += kcals
    currValKcalsDiv.textContent = currValKcals
    currValPercDiv.textContent = Math.round(currValKcals / todaysNormKcals * 100)
}

function clickedDiary(target) {
    // console.log(target.innerText)
    let diaryId = parseInt(target.parentElement.getAttribute('id').replace('diary', ''))
    let diaryFoodName = ''
    let diaryFoodWeight = 0
    // console.log(diaryId)
    floatyEditMainDiv.style.display = 'block'
    for (let i in data[0]) {
        if (data[0][i][0] === diaryId) {
            // console.log(data[0][i])
            diaryFoodName = data[0][i][1]
            diaryFoodWeight = data[0][i][2]
        }
    }
    floatyEditWeight1.value = diaryFoodWeight
    floatyEditFoodName.textContent = diaryFoodName

    floatyEditupdateBtn.addEventListener("click", (event) => { editDiaryUpdate(event.target) });
    floatyEditdeleteBtn.addEventListener("click", () => { editDiaryDelete() });
    floatyEdityesDeleteBtn.addEventListener("click", () => { editDiaryYesDelete(diaryId) });
    floatyEditcancelBtn.addEventListener("click", () => { editDiaryCancel() });
}

function editDiaryUpdate(diaryId) {
}

function editDiaryDelete() {
    floatyEdityesDeleteBtn.style.display = 'block'
}

function editDiaryYesDelete(diaryId) {

    floatyEditMainDiv.style.display = 'none'
    floatyInfoDiv.style.display = 'block'
    floatyInfoText.innerText = 'Ждите...'

    fetch(`/delete_diary_entry/`,
    {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'diary_id': diaryId})
    })
        .then(response => response.json())
        .then(result => {
            console.log(result)
            if (result['result'] == 'success') {
                // console.log('lol, pacan k uspehu prishel xD')
                floatyInfoText.innerText = 'Успешно'
                window.location.reload();
            } else if (result['result'] == 'failure') {
                // console.log('lol, servak zafeililsya xD')
                floatyInfoText.innerText = 'Произошло что-то непонятное, походу все сломалось...'
                window.location.reload();
            }
        })
}












function editDiaryCancel(target) {
    floatyEditMainDiv.style.display = 'none'
    floatyEdityesDeleteBtn.style.display = 'none'
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const isNumeric = (num) => (typeof(num) === 'number' || typeof(num) === "string" && num.trim() !== '') && !isNaN(num);
