const data = JSON.parse(document.getElementById('data').textContent)
console.log(data[0])
initConstr(data)

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
    // const divTableFoot = document.createElement('DIV')
    // const divEmpty1 = document.createElement('DIV')
    // const divEmpty2 = document.createElement('DIV')
    // const divSummary = document.createElement('DIV')
    // const divSumKcals = document.createElement('DIV')
    // const divSumPerc = document.createElement('DIV')
    // divTableFoot.classList.add('row')
    // divEmpty1.classList.add('cell', 'cell-foot')
    // divEmpty2.classList.add('cell', 'cell-foot')
    // divSummary.classList.add('cell', 'cell-foot')
    // divSumKcals.classList.add('cell', 'cell-foot', 'cell-k')
    // divSumPerc.classList.add('cell', 'cell-foot', 'cell-p')
    // divSummary.textContent = `Итого:`
    // divSumKcals.textContent = `${sumKcals}`
    // divSumKcals.classList.add('right')
    // divSumPerc.textContent = `${Math.round(sumKcals / todaysKcals * 100)}`
    // divTableFoot.appendChild(divEmpty1)
    // divTableFoot.appendChild(divSummary)
    // divTableFoot.appendChild(divEmpty2)
    // divTableFoot.appendChild(divSumKcals)
    // divTableFoot.appendChild(divSumPerc)
    // divMainTable.appendChild(divTableFoot)

}

