const data = JSON.parse(document.getElementById('data').textContent)
console.log(data[0])
initConstr(data)

function initConstr(data) {
    const todaysFood = data[0]
    const todaysKcals = data[1]

    const daily_norm_div = document.getElementById('daily_norm')
    daily_norm_div.textContent = `Дневная норма калорий на сегодня: ${todaysKcals} ккал.`

    const divMainTable = document.querySelector('.table')
    const divTableHead = document.createElement('DIV')
    const divNum = document.createElement('DIV')
    const divName = document.createElement('DIV')
    const divWeight = document.createElement('DIV')
    const divKcals = document.createElement('DIV')
    const divPerc = document.createElement('DIV')
    divTableHead.classList.add('row')
    divNum.classList.add('cell')
    divName.classList.add('cell')
    divWeight.classList.add('cell')
    divKcals.classList.add('cell')
    divPerc.classList.add('cell')
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
        divWeight.textContent = `${todaysFood[i][1]} г.`
        divKcals.textContent = `${todaysFood[i][2]} ккал`
        divPerc.textContent = `${Math.round(todaysFood[i][2] / todaysKcals * 100)} %`
        divTableRow.appendChild(divNum)
        divTableRow.appendChild(divName)
        divTableRow.appendChild(divWeight)
        divTableRow.appendChild(divKcals)
        divTableRow.appendChild(divPerc)
        divMainTable.appendChild(divTableRow)
    }
    const divTableFoot = document.createElement('DIV')
    const divEmpty1 = document.createElement('DIV')
    const divEmpty2 = document.createElement('DIV')
    const divSummary = document.createElement('DIV')
    const divSumKcals = document.createElement('DIV')
    const divSumPerc = document.createElement('DIV')
    divTableFoot.classList.add('row')
    divEmpty1.classList.add('cell')
    divEmpty2.classList.add('cell')
    divSummary.classList.add('cell')
    divSumKcals.classList.add('cell')
    divSumPerc.classList.add('cell')
    divSummary.textContent = `Итого:`
    divSumKcals.textContent = `${sumKcals} ккал`
    divSumKcals.classList.add('right')
    divSumPerc.textContent = `${Math.round(sumKcals / todaysKcals * 100)} %`
    divTableFoot.appendChild(divEmpty1)
    divTableFoot.appendChild(divSummary)
    divTableFoot.appendChild(divEmpty2)
    divTableFoot.appendChild(divSumKcals)
    divTableFoot.appendChild(divSumPerc)
    divMainTable.appendChild(divTableFoot)

}

