// function incrementValue() {
//     var value = parseInt(document.getElementById('quantityInput').value, 10);
//     value = isNaN(value) ? 0 : value;
//     value++;
//     document.getElementById('quantityInput').value = value;
// }

// function decrementValue() {
//     var value = parseInt(document.getElementById('quantityInput').value, 10);
//     value = isNaN(value) ? 0 : value;
//     if (value > 1) {
//         value--;
//     }
//     document.getElementById('quantityInput').value = value;
// }

function increment() {
    let quantityInput = document.getElementById("quantity");
    let currentValue = parseInt(quantityInput.value, 10);
    quantityInput.value = currentValue + 1;
}

function decrement() {
    let quantityInput = document.getElementById("quantity");
    let currentValue = parseInt(quantityInput.value, 10);
    if(currentValue > 0) {
        quantityInput.value = currentValue - 1;
    }
}
