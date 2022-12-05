const float_div = document.querySelector('#float-dimming')
const addBtn = document.querySelector('#add-food')
const closeBtn = document.querySelector('#float-cancel')
const inputField = document.querySelector('#float-input')
const resCont = document.querySelector('#float-results-cont')

const data = JSON.parse(document.getElementById('data').textContent)
console.log(data)
// console.log(data[0])
// console.log(data[1])
// console.log(data[2])

let foodDict = {}

onLoad()

function onLoad() {
    initConstr(data)
    // addBtn.addEventListener("click", function clicked(event) { clickAddBtn(event) });
    addBtn.addEventListener("click", function clicked(event) { float_div.style.display = 'block' });
    // closeBtn.addEventListener("click", function clicked(event) { clickCloseBtn(event) });
    closeBtn.addEventListener("click", function clicked(event) { float_div.style.display = 'none' });
    inputField.addEventListener("input", function clicked(event) { changeInput(event.target) });
    foodArrayConsrtuct(data[2])
    console.log(foodDict)
}

function foodArrayConsrtuct(rawFood) {
    for (let i = 0; i < rawFood.length; i++) {
        // console.log(rawFood[i])
        foodDict[rawFood[i][0]] = rawFood[i][1]
    }
}

// function clickAddBtn(event) {
//     // console.log(event)
//     float_div.style.display = 'block'
// }
//
// function clickCloseBtn(event) {
//     // console.log(event)
//     float_div.style.display = 'none'
// }

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
    console.log(tempFoodDict)

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
        }
    }
}

function initConstr(data) {
    const todaysFood = data[0]
    const todaysKcals = data[1]

    const norn_val = document.querySelector('.norm-val')
    norn_val.textContent = todaysKcals

    const divMainTable = document.querySelector('.table')
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
        divNum.textContent = `${i+1}`
        divName.textContent = `${todaysFood[i][0]}`
        divWeight.textContent = `${todaysFood[i][1]}`
        divKcals.textContent = `${todaysFood[i][2]}`
        divPerc.textContent = `${Math.round(todaysFood[i][2] / todaysKcals * 100)}`
        divTableRow.appendChild(divNum)
        divTableRow.appendChild(divName)
        divTableRow.appendChild(divWeight)
        divTableRow.appendChild(divKcals)
        divTableRow.appendChild(divPerc)
        divMainTable.appendChild(divTableRow)
    }
    const curr_val_kcals = document.querySelector('.curr-kcals')
    const curr_val_perc = document.querySelector('.curr-perc')
    curr_val_kcals.textContent = sumKcals
    curr_val_perc.textContent = Math.round(sumKcals / todaysKcals * 100)
}
