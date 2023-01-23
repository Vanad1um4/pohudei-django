const chooseDateInput = document.querySelector('#choose-date')
const thisDateDiv = document.querySelector('.this-date-div')

const divMainTable = document.querySelector('#main-table')
const currValKcalsDiv = document.querySelector('.curr-kcals')
const currValPercDiv = document.querySelector('.curr-perc')

const addBtn = document.querySelector('#add-food')

const thisDaysWeightWarning = document.querySelector('.this-days-weight-warning')
const thisDaysWeightHeader = document.querySelector('.this-days-weight-header')
const thisDaysWeightInput = document.querySelector('.this-days-weight-input')

const floatSearch = document.querySelector('.floaty-search')
const resCont = document.querySelector('.floaty-search-results-cont')
const closeBtn = document.querySelector('.floaty-search-cancel-btn')
const inputSearchField = document.querySelector('.floaty-search-input-field')

const floatyAddNew = document.querySelector('.floaty-add-new')
const floatyAddCont = document.querySelector('.floaty-add-container')
const floatyAddName = document.querySelector('.floaty-add-name')
const floatyAddInput = document.querySelector('.floaty-add-input')
const floatyAddInfo = document.querySelector('.floaty-add-info')
const floatyAddYes = document.querySelector('.floaty-add-yes')
const floatyAddNo = document.querySelector('.floaty-add-no')

const floatyEditMainDiv = document.querySelector('.floaty-edit')
const floatyEditFoodName = document.querySelector('.floaty-edit-header')
const floatyEditWeightNew = document.querySelector('.floaty-edit-weight-input-new')
const floatyEditWeightChange = document.querySelector('.floaty-edit-weight-input-change')
const floatyEditUpdateInfo = document.querySelector('.floaty-edit-update-info')
const floatyEditUpdateBtn = document.querySelector('.floaty-edit-update-btn')
const floatyEditdeleteBtn = document.querySelector('.floaty-edit-delete-btn')
const floatyEdityesDeleteBtn = document.querySelector('.floaty-edit-yes-delete-btn')
const floatyEditcancelBtn = document.querySelector('.floaty-edit-cancel-btn')

const floatyInfoDiv = document.querySelector('.floaty-info')
const floatyInfoText = document.querySelector('.floaty-info-header')

const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
const data = JSON.parse(document.getElementById('data').textContent)
console.log(data)
const thisDaysDateISO = data['dates']['this_day_iso']
const thisDaysFood = data['this_days_food']
const thisDaysNormKcals = data['this_days_target_kcals']
const thisDaysWeight = data['this_days_weight']
// const foodDictRaw = data['all_foods']
const foodArray = data['all_foods']

let currValKcals = 0
let diaryId
let foodDict = {}
let todaysEatenKcals = 0
const waitMsInfo = 500
const waitMsWeightChange = 2000

onLoad()

function onLoad() {
    mainTableOfDiaryEntriesConstruct(data)

    const dateFromString = new Date(thisDaysDateISO)
    const humanDateString = dateFromString.toLocaleString('ru', {month: 'long', day: 'numeric'})
    thisDaysWeightHeader.textContent = `Вес на ${humanDateString}:`
    thisDaysWeightInput.value = thisDaysWeight

    chooseDateInput.addEventListener('input', () => {
        const date = chooseDateInput.value
        if (date) {
            window.location = `/diary/${date}/`
        }
    })

    thisDateDiv.addEventListener("click", () => {
        chooseDateInput.showPicker()
    })

    thisDaysWeightInput.addEventListener('input', () => { saveWeight() })

    addBtn.addEventListener("click", function clicked(event) {
        floatSearch.style.display = 'block'
        inputSearchField.focus()
    })

    closeBtn.addEventListener('click', () => { closeSearch() })
    document.addEventListener('keyup', (event) => {
        if (event.key === 'Escape' && floatSearch.style.display === 'block') {
            closeSearch()
        }
    })

    function closeSearch() {
        floatSearch.style.display = 'none'
        inputSearchField.value = ''

        while (resCont.firstChild) {
            resCont.firstChild.remove()
        }
    }

    floatyAddInput.addEventListener('keyup', function clicked(event) {
        if (event.key === 'Enter') { floatyAddYesPressed(event.target) }
    })

    floatyAddYes.addEventListener("click", function clicked(event) { floatyAddYesPressed(event.target) })

    floatyAddNo.addEventListener("click", function clicked() {
        floatyAddNew.style.display = 'none'
        floatSearch.style.display = 'block'
        inputSearchField.focus()
    })

    document.addEventListener('keyup', function onFirstPress(event) {
        const lettersAndNumbers = '0123456789йцукенгшщзхъфывапролджэячсмитьбю'
        if (floatSearch.style.display !== 'block' &&
            floatyAddNew.style.display !== 'block' &&
            floatyEditMainDiv.style.display !== 'block' &&
            floatyInfoDiv.style.display !== 'block' &&
            thisDaysWeightInput !== document.activeElement) {
            if (event.key.length === 1 && lettersAndNumbers.includes(event.key.toLowerCase())) {
                floatSearch.style.display = 'block'
                inputSearchField.value = event.key
                inputSearchField.focus()
                foodSearchInputUpdate(inputSearchField)
            }
        }
    })

    inputSearchField.addEventListener('input', function typed(event) { foodSearchInputUpdate(event.target) });

    inputSearchField.addEventListener('keyup', function pressed(event) {
        if (event.key === 'Enter') { foodSearchEnterPressed(event.target) }
    })

    floatyEditWeightNew.addEventListener('keyup', function clicked(event) { if (event.key === 'Enter') { editDiaryUpdate() } })
    floatyEditWeightChange.addEventListener('keyup', function clicked(event) { if (event.key === 'Enter') { editDiaryUpdate() } })
    floatyEditUpdateBtn.addEventListener('click', (event) => { editDiaryUpdate() })
    floatyEditdeleteBtn.addEventListener('click', () => { editDiaryDelete() })
    floatyEdityesDeleteBtn.addEventListener('click', (event) => { editDiaryYesDelete() })
    floatyEditcancelBtn.addEventListener('click', () => { editDiaryCancel() })
}

function foodSearchEnterPressed() {
    // console.log(resCont.lastChild)
    foodResultClicked(resCont.lastChild)
}

async function saveWeight() {
    const lastVal = thisDaysWeightInput.value
    await sleep(waitMsWeightChange)
    const newVal = thisDaysWeightInput.value
    if (lastVal === newVal) {
        if (!(numTest(newVal))) {
            thisDaysWeightWarning.style.display = 'block'
            thisDaysWeightWarning.textContent = 'Вес должен быть в формате 99.9'
        } else {
            thisDaysWeightInput.disabled = true
            thisDaysWeightInput.style.background = 'rgb(192 192 192 / 66%)'

            fetch(`/update_weight/`,
            {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({'date': thisDaysDateISO, 'weight': newVal})
            })
                .then(response => response.json())
                .then(result => {
                    if (result['result'] === 'success') {
                        console.log('success')
                        thisDaysWeightInput.disabled = false
                        thisDaysWeightInput.style.background = 'green'
                        thisDaysWeightWarning.style.display = 'none'
                    } else if (result['result'] === 'failure') {
                        console.log('failure')
                        thisDaysWeightInput.disabled = false
                        thisDaysWeightInput.style.background = 'red'
                        // thisDaysWeightWarning.style.display = 'none'
                        thisDaysWeightWarning.textContent = 'Что-то пошло не так...'
                    }
                })
                .then(await sleep(waitMsWeightChange))
                .then(() => { thisDaysWeightInput.style.background = 'transparent' })
        }
    }
}

function foodSearchInputUpdate(target) {
    const queryArray = target.value.toLowerCase().split(' ').filter(val => val.length > 0)
    // console.log(queryArray)

    let tempFoodArray = []
    for (let i in foodArray) {
        if (queryArray.every(word => foodArray[i][1].toLowerCase().includes(word))){
            tempFoodArray.push([foodArray[i][0], foodArray[i][1]])
        }
    }

    while (resCont.firstChild) {
        resCont.firstChild.remove()
    }

    for (let i in tempFoodArray) {
        // console.log(tempFoodArray[i])
        const resDiv = document.createElement('DIV')
        resDiv.classList.add('float-results-line')
        resDiv.setAttribute('id', 'food' + tempFoodArray[i][0])
        resDiv.textContent = `${tempFoodArray[i][1]}`
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
        floatyInfoText.style.color = 'white'
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
        body: JSON.stringify({'date_iso': thisDaysDateISO, 'food_id': foodId, 'food_weight': newWeight})
    })
        .then(response => response.json())
        .then(result => {
            if (result['result'] == 'success') {
                floatyInfoText.textContent = 'Успешно!'
                floatyInfoText.style.color = 'LawnGreen'
            } else if (result['result'] == 'failure') {
                floatyInfoText.textContent = 'Произошло что-то непонятное, походу все сломалось...'
                floatyInfoText.style.color = 'red'
            }
        })
        .then(await sleep(waitMsInfo))
        .then(() => { window.location.reload() })
}


///// MAIN TABLE FUNCTIONS ////////////////////////////////////////////////////


function mainTableOfDiaryEntriesConstruct() {
    const normVal = document.querySelector('.norm-val')
    normVal.textContent = thisDaysNormKcals

    const divTableHead = document.createElement('DIV')
    const divName = document.createElement('DIV')
    const divWeight = document.createElement('DIV')
    const divKcals = document.createElement('DIV')
    const divPerc = document.createElement('DIV')
    divTableHead.classList.add('row')
    divName.classList.add('cell', 'cell-head', 'cell-name')
    divWeight.classList.add('cell', 'cell-head')
    divKcals.classList.add('cell', 'cell-head')
    divPerc.classList.add('cell', 'cell-head')
    divName.textContent = 'Блюдо'
    divWeight.textContent = 'Вес'
    divKcals.textContent = 'Ккал'
    divPerc.textContent = '%'
    divTableHead.appendChild(divName)
    divTableHead.appendChild(divWeight)
    divTableHead.appendChild(divKcals)
    divTableHead.appendChild(divPerc)
    divMainTable.appendChild(divTableHead)

    divTableHead.addEventListener("click", (event) => { copyTable() });

    currValKcalsDiv.textContent = 0
    currValPercDiv.textContent = 0

    for (let i = 0; i < thisDaysFood.length; i++) {
        addRow(thisDaysFood[i][0], thisDaysFood[i][1], thisDaysFood[i][2], thisDaysFood[i][3], thisDaysNormKcals)
    }
}


function addRow(id, name, weight, kcals, thisDaysNormKcals) {
    const divTableRow = document.createElement('DIV')
    const divName = document.createElement('DIV')
    const divWeight = document.createElement('DIV')
    const divKcals = document.createElement('DIV')
    const divPerc = document.createElement('DIV')
    divTableRow.classList.add('row')
    divTableRow.setAttribute('id', 'diary' + id)
    divName.classList.add('cell', 'cell-name')
    divWeight.classList.add('cell', 'cell-w')
    divKcals.classList.add('cell', 'cell-k')
    divPerc.classList.add('cell', 'cell-p')
    divName.textContent = `${name}`
    divWeight.textContent = `${weight}`
    divKcals.textContent = `${kcals}`
    const percent = Math.round(kcals / thisDaysNormKcals * 100)
    divPerc.textContent = `${percent}`
    divTableRow.appendChild(divName)
    divTableRow.appendChild(divWeight)
    divTableRow.appendChild(divKcals)
    divTableRow.appendChild(divPerc)
    divMainTable.appendChild(divTableRow)

    divTableRow.addEventListener("click", (event) => { clickedDiary(event.target) });
    divTableRow.style.backgroundImage = `linear-gradient(to right, #c5cfff ${percent}%, #ffffff 0%)`;

    currValKcals += kcals
    currValKcalsDiv.textContent = currValKcals
    currValPercDiv.textContent = Math.round(currValKcals / thisDaysNormKcals * 100)
}


///// CHANGE DIARY ENTRY FUNCTIONS ////////////////////////////////////////////


function clickedDiary(target) {
    diaryId = parseInt(target.parentElement.getAttribute('id').replace('diary', ''))
    let diaryFoodName = ''
    let diaryFoodWeight = 0
    floatyEditMainDiv.style.display = 'block'
    for (let i in thisDaysFood) {
        if (thisDaysFood[i][0] === diaryId) {
            diaryFoodName = thisDaysFood[i][1]
            diaryFoodWeight = thisDaysFood[i][2]
        }
    }
    floatyEditWeightNew.value = diaryFoodWeight
    floatyEditFoodName.textContent = diaryFoodName
    floatyEditWeightChange.focus()
}

async function editDiaryUpdate() {
    const weightOrig = parseInt(floatyEditWeightNew.value)
    let weightChange = parseInt(floatyEditWeightChange.value)
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
        floatyInfoText.style.color = 'white'

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
            floatyInfoText.textContent = 'Успешно!'
            floatyInfoText.style.color = 'LawnGreen'
        } else if (result['result'] == 'failure') {
            floatyInfoText.textContent = 'Произошло что-то непонятное, походу все сломалось...'
            floatyInfoText.style.color = 'red'
        }
    })
    .then(await sleep(waitMsInfo))
    .then(() => { window.location.reload() })
}

function editDiaryDelete() {
    floatyEdityesDeleteBtn.style.display = 'block'
}

async function editDiaryYesDelete() {
    floatyEditMainDiv.style.display = 'none'
    floatyInfoDiv.style.display = 'block'
    floatyInfoText.textContent = 'Ждите...'
    floatyInfoText.style.color = 'white'

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
                floatyInfoText.textContent = 'Успешно!'
                floatyInfoText.style.color = 'LawnGreen'
            } else if (result['result'] == 'failure') {
                floatyInfoText.textContent = 'Произошло что-то непонятное, походу все сломалось...'
                floatyInfoText.style.color = 'red'
            }
        })
        .then(await sleep(waitMsInfo))
        .then(() => { window.location.reload() })
}



function editDiaryCancel() {
    floatyEditMainDiv.style.display = 'none'
    floatyEdityesDeleteBtn.style.display = 'none'
}


///// TABLE COPY FUNCTIONS ////////////////////////////////////////////////////


function copyTable() {
    const today = new Date(thisDaysDateISO)
    const humanToday = today.toLocaleDateString('ru')
    let resultString = ''
    for (let i in thisDaysFood) {
        resultString += humanToday
        resultString += '\t'
        resultString += thisDaysFood[i][1] + ' NEW'
        resultString += '\t'
        resultString += thisDaysFood[i][2]
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


// function foodDictPrep() {
//     let resultDict = {}
//     for (let i = 0; i < foodDictRaw.length; i++) {
//         resultDict[foodDictRaw[i][0]] = foodDictRaw[i][1]
//     }
//     return resultDict
// }

function sleep(ms) {return new Promise(resolve => setTimeout(resolve, ms));}

function numTest(num) {
    const regex = new RegExp(/^\b[\d]{2,3}[.][\d]{1}\b$|^\b[\d]{2,3}\b$/gm)
    return regex.test(num)
}
const isNumeric = (num) => (typeof(num) === 'number' || typeof(num) === "string" && num.trim() !== '') && !isNaN(num);
