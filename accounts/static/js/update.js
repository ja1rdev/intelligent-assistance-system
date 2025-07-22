// Initialize DOM references and variables for facial recognition update
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureButton = document.getElementById('capture-button');
const updateForm = document.getElementById('update-form');
const message = document.getElementById('message');
let capturedImage = null;

// Access the camera and start the video stream
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        message.innerText = 'Camera enabled successfully.';
    })
    .catch(error => {
        console.error('Error accessing camera:', error);
        message.innerText = 'Camera not accessible. Please check permissions.';
    });

// Check if camera is active
captureButton.addEventListener('click', () => {
    if (!video.srcObject) {
        message.innerText = "Please enable the camera.";
        return;
    }

    // Handle different aspect ratios, especially for mobile
    const context = canvas.getContext('2d');
    const videoWidth = video.videoWidth;
    const videoHeight = video.videoHeight;
    const canvasAspectRatio = canvas.width / canvas.height;
    const videoAspectRatio = videoWidth / videoHeight;

    let drawX = 0, drawY = 0, drawWidth = canvas.width, drawHeight = canvas.height;

    if (videoAspectRatio > canvasAspectRatio) {
        // Video is wider than canvas
        drawHeight = canvas.width / videoAspectRatio;
        drawY = (canvas.height - drawHeight) / 2;
    } else {
        // Video is taller than canvas
        drawWidth = canvas.height * videoAspectRatio;
        drawX = (canvas.width - drawWidth) / 2;
    }

    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(video, drawX, drawY, drawWidth, drawHeight);

    capturedImage = canvas.toDataURL('image/jpeg', 0.9);
    message.innerText = "Image captured successfully.";
});

// Handle update form submission and send user data with face image
updateForm.onsubmit = async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const identification_number = document.getElementById('identification_number').value;
    const user_type = document.getElementById('user_type').value;

    if (!username || !identification_number || !user_type) {
        message.innerText = "Please fill all required fields";
        return;
    }

    const formData = new FormData(updateForm);
    if (capturedImage) {
        formData.append('face_image', capturedImage);
    }

    const response = await fetch(updateForm.action, {
        method: "POST",
        body: formData,
    });

    const data = await response.json();
    if (data.status == 'success') {
        message.innerText = data.message || 'Update successful!';
        if (data.redirect) {
            setTimeout(() => {
                window.location.href = data.redirect;
            }, 1000);
        }
    } else {
        message.innerText = data.message || 'Update failed.'
    }
} 