// TODO: refactor the sh*t out of it

const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

const divMainTable = document.querySelector('#main-table')
const currValKcalsDiv = document.querySelector('.curr-kcals')
let currValKcals = 0
const currValPercDiv = document.querySelector('.curr-perc')

const floatSearch = document.querySelector('#float-dimming-search')
const addBtn = document.querySelector('#add-food')
const closeBtn = document.querySelector('#float-cancel')
const inputSearchField = document.querySelector('#float-input')
const resCont = document.querySelector('#float-results-container')

const floatyAddNew = document.querySelector('#floaty-add-new')
const floatyAddInput = document.querySelector('#floaty-add-input')
const floatyAddInfo = document.querySelector('#floaty-add-info')
const floatyInfoDiv = document.querySelector('#floaty-info-div')
const floatyInfoText = document.querySelector('#floaty-info-text')

const floatyAddCont = document.querySelector('#floaty-add-cont')
const floatyAddName = document.querySelector('#floaty-add-name')
const floatyAddYes = document.querySelector('#floaty-add-yes')
const floatyAddNo = document.querySelector('#floaty-add-no')

const floatyEditCont = document.querySelector('.floaty-edit-cont')
const floatyEditMainDiv = document.querySelector('#floaty-edit')
const floatyEditFoodName = document.querySelector('#name-food')
const floatyEditWeightOrig = document.querySelector('#edit-weight-input-curr')
const floatyEditWeightChange = document.querySelector('#edit-weight-input-change')
const floatyEditUpdateInfo = document.querySelector('#update-info')
const floatyEditUpdateBtn = document.querySelector('#update-btn')
const floatyEditdeleteBtn = document.querySelector('#delete-btn')
const floatyEdityesDeleteBtn = document.querySelector('#yes-delete-btn')
const floatyEditcancelBtn = document.querySelector('#edit-cancel-btn')
let diaryId

const data = JSON.parse(document.getElementById('data').textContent)
console.log(data)
const todaysFood = data[0]
const todaysNormKcals = data[1]
let todaysEatenKcals = 0
let foodDict = {}
// const waitMs = 1000
const waitMs = 0

onLoad()

function onLoad() {
    mainTableOfDiaryEntriesConstruct(data)

    addBtn.addEventListener("click", function clicked(event) {
        floatSearch.style.display = 'block'
        inputSearchField.focus()
    });

    closeBtn.addEventListener("click", function clicked(event) {
        floatSearch.style.display = 'none'
        inputSearchField.value = ''

        while (resCont.firstChild) {
            resCont.firstChild.remove()
        }


    });

    floatyAddInput.addEventListener("keyup", function clicked(event) {
        if (event.key === 'Enter') { floatyAddYesPressed(event.target) }
    })

    floatyAddYes.addEventListener("click", function clicked(event) { floatyAddYesPressed(event.target) })

    floatyAddNo.addEventListener("click", function clicked() {
        floatyAddNew.style.display = 'none'
        floatSearch.style.display = 'block'
        inputSearchField.focus()
    })

    inputSearchField.addEventListener("input", function clicked(event) { foodSearchInputUpdate(event.target) });



    floatyEditWeightChange.addEventListener("keyup", function clicked(event) {
        if (event.key === 'Enter') { editDiaryUpdate(event.target) } })

    floatyEditUpdateBtn.addEventListener("click", (event) => { editDiaryUpdate(event.target) });

    floatyEditdeleteBtn.addEventListener("click", () => { editDiaryDelete() });

    floatyEdityesDeleteBtn.addEventListener("click", (event) => { editDiaryYesDelete(event.target) });

    floatyEditcancelBtn.addEventListener("click", () => { editDiaryCancel() });

    foodDict = foodDictConsrtuct(data[2])
}

function foodSearchInputUpdate(target) {
    const queryArray = target.value.toLowerCase().split(' ').filter(val => val.length > 0)

    let tempFoodDict = {}
    for (let i in foodDict) {
        if (queryArray.every(word => foodDict[i].toLowerCase().includes(word))){
            tempFoodDict[i] = foodDict[i]
        }
    }

    while (resCont.firstChild) {
        resCont.firstChild.remove()
    }

    for (let i in tempFoodDict) {
        const resDiv = document.createElement('DIV')
        resDiv.classList.add('float-results-line')
        resDiv.setAttribute('id', 'food' + i)
        resDiv.textContent = `${tempFoodDict[i]}`
        resCont.appendChild(resDiv)

        resDiv.addEventListener("click", function clicked(event) { foodResultClicked(event.target) });
    }
}

function foodResultClicked(target) {
    let foodId = parseInt(target.getAttribute('id').replace('food', ''))
    floatSearch.style.display = 'none'

    floatyAddCont.setAttribute('name', 'food' + foodId)

    floatyAddName.textContent = target.textContent
    floatyAddInfo.textContent = 'Введите вес блюда:'

    floatyAddInput.value = ''

    floatyAddNew.style.display = 'block'

    floatyAddInput.focus()
}

async function floatyAddYesPressed(target) {
    const foodId = parseInt(target.parentElement.parentElement.getAttribute('name').replace('food', ''))
    const newWeight = parseInt(floatyAddInput.value)
    if (newWeight === '') {
        floatyAddInfo.textContent = 'Вы не ввели вес!'
    } else if (!(/^\d+$/.test(newWeight))) {
        floatyAddInfo.textContent = 'Введите только цифры, граммы, целое цисло!'
    }
    else {
        floatyAddNew.style.display = 'none'
        floatyInfoDiv.style.display = 'block'
        floatyInfoText.textContent = 'Ждите...'
        fetchAdd(foodId, newWeight)
    }
}

async function fetchAdd(foodId, newWeight) {
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
            if (result['result'] == 'success') {
                floatyInfoText.textContent = 'Успешно'
            } else if (result['result'] == 'failure') {
                floatyInfoText.textContent = 'Произошло что-то непонятное, походу все сломалось...'
            }
        })
        .then(await sleep(waitMs))
        .then(() => { window.location.reload() })
}


///// MAIN TABLE FUNCTIONS ////////////////////////////////////////////////////


function mainTableOfDiaryEntriesConstruct() {
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
    divName.classList.add('cell', 'cell-head', 'cell-name')
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

    divTableHead.addEventListener("click", (event) => { copyTable() });

    currValKcalsDiv.textContent = 0
    currValPercDiv.textContent = 0

    for (let i = 0; i < todaysFood.length; i++) {
        // addRow(i+1, todaysFood[i][0], todaysFood[i][1], todaysFood[i][2], todaysNormKcals)
        addRow(todaysFood[i][0], todaysFood[i][1], todaysFood[i][2], todaysFood[i][3], todaysNormKcals)
    }
}


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
    const percent = Math.round(kcals / todaysNormKcals * 100)
    divPerc.textContent = `${percent}`
    // divTableRow.appendChild(divNum)
    divTableRow.appendChild(divName)
    divTableRow.appendChild(divWeight)
    divTableRow.appendChild(divKcals)
    divTableRow.appendChild(divPerc)
    divMainTable.appendChild(divTableRow)

    divTableRow.addEventListener("click", (event) => { clickedDiary(event.target) });
    divTableRow.style.backgroundImage = `linear-gradient(to right, #D2FFC9 ${percent}%, #FFFFFF ${percent}%)`;

    currValKcals += kcals
    currValKcalsDiv.textContent = currValKcals
    currValPercDiv.textContent = Math.round(currValKcals / todaysNormKcals * 100)
}


///// CHANGE DIARY ENTRY FUNCTIONS ////////////////////////////////////////////


function clickedDiary(target) {
    diaryId = parseInt(target.parentElement.getAttribute('id').replace('diary', ''))
    floatyEditCont.setAttribute('name', 'diary' + diaryId)
    // floatyEditUpdateBtn.setAttribute('name', 'diary' + diaryId)
    // floatyEdityesDeleteBtn.setAttribute('name', 'diary' + diaryId)
    let diaryFoodName = ''
    let diaryFoodWeight = 0
    floatyEditMainDiv.style.display = 'block'
    for (let i in data[0]) {
        if (data[0][i][0] === diaryId) {
            diaryFoodName = data[0][i][1]
            diaryFoodWeight = data[0][i][2]
        }
    }
    floatyEditWeightOrig.value = diaryFoodWeight
    floatyEditFoodName.textContent = diaryFoodName
    floatyEditWeightChange.focus()
}

async function editDiaryUpdate(target) {
    // console.log(target.parentElement.parentElement.parentElement.parentElement)
    // let diaryId = parseInt(target.parentElement.parentElement.parentElement.parentElement.getAttribute('name').replace('diary', ''))
    // console.log(diaryId)
    const weightOrig = parseInt(floatyEditWeightOrig.value)
    let weightChange = parseInt(floatyEditWeightChange.value)
    // console.log(weightChange)
    if (!(isNumeric(weightChange))){weightChange = 0}
    const resultWeight = weightOrig + weightChange
    floatyEditUpdateInfo.style.display = 'none'
    if (resultWeight == 0) {
        floatyEditUpdateInfo.style.display = 'block'
        floatyEditUpdateInfo.textContent = 'Ноль? Если Вы хотите удалить запись, то ниже есть кнопка "Удалить" :)'
    } else if (resultWeight < 0) {
        floatyEditUpdateInfo.style.display = 'block'
        floatyEditUpdateInfo.textContent = 'Ожидается, что вес будет положительным значением :)'
    } else if (!(isNumeric(resultWeight))) {
        floatyEditUpdateInfo.style.display = 'block'
        floatyEditUpdateInfo.textContent = 'Вводите только цифры :)'
    } else {
        floatyEditMainDiv.style.display = 'none'
        floatyInfoDiv.style.display = 'block'
        floatyInfoText.textContent = 'Ждите...'

        fetchEdit(diaryId, resultWeight)
    }
}

async function fetchEdit(id, weight) {
    fetch(`/update_diary_entry/`,
    {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'diary_id': id, 'new_weight': weight})
    })
    .then(response => response.json())
    .then(result => {
        if (result['result'] == 'success') {
            floatyInfoText.textContent = 'Успешно'
        } else if (result['result'] == 'failure') {
            floatyInfoText.textContent = 'Произошло что-то непонятное, походу все сломалось...'
        }
    })
    .then(await sleep(waitMs))
    .then(() => { window.location.reload() })
}

function editDiaryDelete() {
    floatyEdityesDeleteBtn.style.display = 'block'
}

async function editDiaryYesDelete(target) {
    // console.log(target.parentElement.parentElement)
    // let diaryId = parseInt(target.getAttribute('name').replace('diary', ''))
    // let diaryId = parseInt(target.parentElement.parentElement.getAttribute('name').replace('diary', ''))

    floatyEditMainDiv.style.display = 'none'
    floatyInfoDiv.style.display = 'block'
    floatyInfoText.textContent = 'Ждите...'

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
            if (result['result'] == 'success') {
                floatyInfoText.textContent = 'Успешно'
            } else if (result['result'] == 'failure') {
                floatyInfoText.textContent = 'Произошло что-то непонятное, походу все сломалось...'
            }
        })
        .then(await sleep(waitMs))
        .then(() => { window.location.reload() })
}



function editDiaryCancel(target) {
    floatyEditMainDiv.style.display = 'none'
    floatyEdityesDeleteBtn.style.display = 'none'
}


///// TABLE COPY FUNCTIONS ////////////////////////////////////////////////////


function copyTable() {
    const today = new Date(Date.now())
    const humanToday = today.toLocaleDateString('ru')
    let resultString = ''
    for (let i in data[0]) {
        resultString += humanToday
        resultString += '\t'
        resultString += data[0][i][1] + ' NEW'
        resultString += '\t'
        resultString += data[0][i][2]
        resultString += '\n'
    }
    const input = document.createElement('textarea');
    input.innerHTML = resultString;
    document.body.appendChild(input);
    input.select();
    const result = document.execCommand('copy');
    document.body.removeChild(input);
    // console.log(result)
}


///// OTHER FUNCTIONS /////////////////////////////////////////////////////////


function foodDictConsrtuct(inputFoodDict) {
    let resultDict = {}
    for (let i = 0; i < inputFoodDict.length; i++) {
        resultDict[inputFoodDict[i][0]] = inputFoodDict[i][1]
    }
    return resultDict
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const isNumeric = (num) => (typeof(num) === 'number' || typeof(num) === "string" && num.trim() !== '') && !isNaN(num);
