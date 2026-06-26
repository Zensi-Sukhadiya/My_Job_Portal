document.getElementById('improve-ai-btn').addEventListener('click', async function () {
    const desc = document.getElementById('job-description').value;
    if (!desc) {
        alert("Please enter some description first.");
        return;
    }

    this.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-4"></i> Improving...';
    this.disabled = true;

    try {
        const response = await fetch("{% url 'improve_description' %}", 
        {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ description: desc })
        });
        const data = await response.json();
        document.getElementById('job-description').value = data.improved_description;
    } catch (error) {
        console.error('Error:', error);
        alert("Failed to improve description.");
    } finally {
        this.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles mr-4"></i> Improve with AI';
        this.disabled = false;
    }
});


function updateFileName(input) {
    const fileName = input.files[0] ? input.files[0].name : "Upload Company Logo";
    document.getElementById('upload-filename').textContent = fileName;
    if (input.files[0]) {
      document.querySelector('.upload-area').style.borderColor = 'var(--primary)';
      document.querySelector('.upload-area').style.background = 'var(--primary-light)';
    }
  }


// Edit_job
document.getElementById('improve-ai-btn').addEventListener('click', async function () {
    const desc = document.getElementById('job-description').value;
    if (!desc) {
        alert("Please enter some description first.");
        return;
    }

    this.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-4"></i> Improving...';
    this.disabled = true;

    try {
        const response = await fetch("{% url 'improve_description' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({ description: desc })
        });
        const data = await response.json();
        document.getElementById('job-description').value = data.improved_description;
    } catch (error) {
        console.error('Error:', error);
        alert("Failed to improve description.");
    } finally {
        this.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles mr-4"></i> Improve with AI';
        this.disabled = false;
    }
});


function updateFileName(input) {
    const fileName = input.files[0] ? input.files[0].name : "{% if job.logo %}Change Logo{% else %}Upload Company Logo{% endif %}";
    document.getElementById('upload-filename').textContent = fileName;
    if (input.files[0]) {
        document.querySelector('.upload-area').style.borderColor = 'var(--primary)';
        document.querySelector('.upload-area').style.background = 'var(--primary-light)';

        // If there was an image, hide it or replace with icon for consistency while showing name
        const iconBox = document.querySelector('.upload-icon-large');
        if (input.files[0].type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function (e) {
                iconBox.innerHTML = `<img src="${e.target.result}" style="width: 48px; height: 48px; border-radius: 8px; object-fit: cover;">`;
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
}