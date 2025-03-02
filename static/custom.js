document.addEventListener('DOMContentLoaded', function() {
    // JavaScript to handle image swapping
    document.querySelectorAll('.smallCard').forEach(img => {
        img.addEventListener('click', function() {
            document.getElementById('largeCard').src = this.src;
            document.getElementById('largeCardDetails').innerHTML = 'Name: ' + this.dataset.name + '<p>' + 'Valued at: ' + this.dataset.cost + '</p>';
        });
    });



    // Sell Form selection
    const sellForm = document.getElementById('sell-form');
    if (sellForm) {
        sellForm.addEventListener('submit', function(event) {
            // Prevent the form from submitting immediately
            event.preventDefault();

            // Collect data from selected checkboxes
            const selectedCards = [];
            const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
            checkboxes.forEach(checkbox => {
                const card_id = checkbox.value;
                const price = document.getElementById(`price${card_id}`).value;
                const quantity = document.getElementById(`quantity${card_id}`).value;
                selectedCards.push({ card_id, price, quantity });
            });

            // Send the selected cards data to app.py. Code from chatGPT
            fetch('/sell', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ selectedCards: selectedCards })
            })
            .then(response => response.json())
            .then(data => {
                // Handle the server response here
                console.log('Success:', data);
                // You can also redirect the user, show a success message, etc.
                // Redirect to the sell page to show the flash message
                window.location.href = '/sellpage';
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
    }

    // Validate maximum quantity
    document.querySelectorAll("input[name='quantity']").forEach(input => {
        input.addEventListener('input', function() {
            const maxQuantity = parseInt(this.getAttribute('data-quantity'), 10); //Specify base number when using parseInt
            const currentQuantity = parseInt(this.value, 10);

            if (currentQuantity > maxQuantity) {
                alert(`You cannot sell more than ${maxQuantity} of this card.`);
                this.value = maxQuantity;
            } else if (currentQuantity < 1) {
                alert("Quantity must be at least 1.");
                this.value = 1;
            }
        });
    });

    // Function to calculate and update total cost
    function updateTotalCost() {
        console.log("Checkbox changed!");
        let totalCost = 0;
        const gems = parseInt(document.getElementById('user-gems').value, 10);
        document.querySelectorAll(".checkbox:checked").forEach(checkedBox => {
            const price = parseInt(checkedBox.getAttribute('data-price'), 10);
            if (!isNaN(price)) {
                totalCost += price;
            }
        });
        document.getElementById('total-cost').innerText = 'Total Cost: ' + totalCost + " Gems";
        if (totalCost > gems) {
            alert('You do not have enough Gems!')
            document.querySelector('button[type="submit"]').disabled = true;
        } else {
            document.querySelector('button[type="submit"]').disabled = false;
        }
    };

    // Add event listener to checkboxes
    document.querySelectorAll(".checkbox").forEach(checkbox => {
        checkbox.addEventListener('change', updateTotalCost);
    });

    // Buy Form Submission
    document.getElementById('buy-form').addEventListener('submit', function(event) {
        // Prevent the form from submitting immediately
        event.preventDefault();

        // Collect data from selected checkboxes
        const selectedCards = [];
        const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
        checkboxes.forEach(checkbox => {
            //const price = document.getElementById(`price${card_id}`).value;
            const sale_id = checkbox.getAttribute('data-sale-id');
            selectedCards.push({ sale_id });
        });

        // Send the selected cards data to app.py. Code from chatGPT
        fetch('/buy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ selectedCards: selectedCards })
        })
        .then(response => response.json())
        .then(data => {
            // Handle the server response here
            console.log('Success:', data);
            // You can also redirect the user, show a success message, etc.
            // Redirect to the buy page to show the flash message
            window.location.href = '/buy';
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});
