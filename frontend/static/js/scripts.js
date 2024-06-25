/**
 * Update the slider value display position and text.
 */
function updateSliderValue(value) {
    const sliderValue = document.getElementById('sliderValue');
    const slider = document.getElementById('popularityRange');
    const sliderMax = slider.max;
    const sliderWidth = slider.offsetWidth;
    const newLeft = (value / sliderMax) * sliderWidth;
    sliderValue.style.left = `${newLeft}px`;
    sliderValue.innerText = value;
}

// Event listener for form submission
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('searchForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);
        fetch('/search', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.redirect) {
                window.location.href = data.redirect;
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Event listener for slider input
    document.getElementById('popularityRange').addEventListener('input', function() {
        updateSliderValue(this.value);
    });
});
