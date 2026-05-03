/*
2. Фільтр JSON

Напишіть програму, яка приймає JSON-файл та значення фільтра в якості вхідних даних.
• Програма повинна фільтрувати дані JSON, залишаючи лише ті елементи, які відповідають заданому значенню фільтра.
• Виведіть відфільтровані дані JSON.
*/

const fs = require("fs");

const fileName = process.argv[2];
const fieldName = process.argv[3];
const filterValue = process.argv[4];

if (!fileName || !fieldName || !filterValue) {
    console.log("Usage: node filter-json.js <fileName> <fieldName> <filterValue>");
    process.exit(1);
}

const jsonText = fs.readFileSync(fileName, "utf-8");
const data = JSON.parse(jsonText);

if (!Array.isArray(data)) {
    console.log("JSON file must contain an array of objects.");
    process.exit(1);
}

const filteredData = data.filter(item => {
    return String(item[fieldName]).toLowerCase() === filterValue.toLowerCase();
});

console.log(JSON.stringify(filteredData, null, 2));

// node task2.js test.json lastRecord 1928
