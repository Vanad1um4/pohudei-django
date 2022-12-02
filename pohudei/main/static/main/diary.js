const data = JSON.parse(document.getElementById('data').textContent)
console.log(data[0])
initConstr(data)

function initConstr(data) {
    const todaysFood = data[0]
    const todaysKcals = data[1]

    const daily_norm_div = document.getElementById('daily_norm')
    daily_norm_div.textContent = `Дневная норма калорий на сегодня: ${todaysKcals} ккал.`

    const table = document.getElementById('main_table')
    const tr = document.createElement('TR')
    const thNum = document.createElement('TH')
    const thName = document.createElement('TH')
    const thWeight = document.createElement('TH')
    const thKcals = document.createElement('TH')
    const thPerc = document.createElement('TH')
    thNum.textContent = '№'
    thName.textContent = 'Блюдо'
    thWeight.textContent = 'Вес'
    thKcals.textContent = 'Ккал'
    thPerc.textContent = '%'
    tr.appendChild(thNum)
    tr.appendChild(thName)
    tr.appendChild(thWeight)
    tr.appendChild(thKcals)
    tr.appendChild(thPerc)
    table.appendChild(tr)

    let sumKcals = 0
    for (let i = 0; i < todaysFood.length; i++) {
        sumKcals += todaysFood[i][2]
        const tr = document.createElement('TR')
        const tdNum = document.createElement('TD')
        const tdName = document.createElement('TD')
        const tdWeight = document.createElement('TD')
        const tdKcals = document.createElement('TD')
        const tdPerc = document.createElement('TD')
        tdNum.classList.add('center')
        tdName.classList.add('left')
        tdWeight.classList.add('right')
        tdKcals.classList.add('right')
        tdPerc.classList.add('right')
        tdNum.textContent = `${i+1}`
        tdName.textContent = `${todaysFood[i][0]}`
        tdWeight.textContent = `${todaysFood[i][1]} г.`
        tdKcals.textContent = `${todaysFood[i][2]} ккал`
        tdPerc.textContent = `${Math.round(todaysFood[i][2] / todaysKcals * 100)} %`
        tr.appendChild(tdNum)
        tr.appendChild(tdName)
        tr.appendChild(tdWeight)
        tr.appendChild(tdKcals)
        tr.appendChild(tdPerc)
        table.appendChild(tr)
    }
    const trBottom = document.createElement('TR')
    const tdEmpty1 = document.createElement('TD')
    const tdEmpty2 = document.createElement('TD')
    const tdSummary = document.createElement('TD')
    const tdSumKcals = document.createElement('TD')
    const tdSumPerc = document.createElement('TD')
    tdSummary.textContent = `Итого:`
    tdSumKcals.textContent = `${sumKcals} ккал`
    tdSumKcals.classList.add('right')
    tdSumPerc.textContent = `${Math.round(sumKcals / todaysKcals * 100)} %`
    trBottom.appendChild(tdEmpty1)
    trBottom.appendChild(tdSummary)
    trBottom.appendChild(tdEmpty2)
    trBottom.appendChild(tdSumKcals)
    trBottom.appendChild(tdSumPerc)
    table.appendChild(trBottom)

}

