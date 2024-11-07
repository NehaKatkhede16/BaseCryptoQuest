document.getElementById('join-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const address = document.getElementById('address').value;

    const response = await fetch('/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `address=${address}`
    });

    const result = await response.json();
    alert(result.message);
});
