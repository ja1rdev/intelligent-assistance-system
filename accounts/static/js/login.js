// Initialize DOM references and variables for facial recognition login
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const message = document.getElementById('message');
const userInfo = document.getElementById('user-info');
const csrftoken = document.getElementById('csrf-token').value;
const usernameDisplay = document.getElementById('username-display');
const entryButton = document.getElementById('entry-button');
const exitButton = document.getElementById('exit-button');

let capturedImage = null;
let faceDetectionInterval = null;
let recognizedUsername = null;
let lastDetectionAttempt = 0;
const DETECTION_INTERVAL = 3000;

// Function to update the message display with different alert types
function updateMessage(text, type = 'info') {
    message.innerText = text;
    message.classList.remove('alert-success', 'alert-danger', 'alert-info');
    switch (type) {
        case 'success':
            message.classList.add('alert-success');
            break;
        case 'error':
            message.classList.add('alert-danger');
            break;
        case 'info':
        default:
            message.classList.add('alert-info');
    }
    message.style.display = 'block';
}

// Start periodic face detection using the video stream 
function startFaceDetection() {
    updateMessage('Looking for faces... Please look at the camera.', 'info');
    if (faceDetectionInterval) {
        clearInterval(faceDetectionInterval);
    }
    faceDetectionInterval = setInterval(() => {
        if (!recognizedUsername) {
            const now = Date.now();
            if (now - lastDetectionAttempt > DETECTION_INTERVAL) {
                lastDetectionAttempt = now;
                detectFace();
            }
        }
    }, 1000);
}

// Capture an image from the video stream and process it for face detection
function detectFace() {
    updateMessage('Processing face...', 'info');
    const context = canvas.getContext('2d');

    // Handle different aspect ratios, especially for mobile
    const videoWidth = video.naturalWidth;
    const videoHeight = video.naturalHeight;
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
    sendImageForRecognition();
}

// Send the captured image to the server for face recognition
async function sendImageForRecognition() {
    if (!capturedImage) {
        updateMessage('No image captured.', 'error');
        return;
    }
    const formData = new FormData();
    formData.append("face_image", capturedImage);
    try {
        const response = await fetch('/login/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrftoken
            }
        });
        const data = await response.json();
        if (data.status === 'success') {
            recognizedUsername = data.username;
            usernameDisplay.textContent = recognizedUsername;
            userInfo.style.display = 'block';
            updateMessage(data.message || `Welcome ${recognizedUsername}!`, 'success');
            if (faceDetectionInterval) {
                clearInterval(faceDetectionInterval);
            }
        } else {
            updateMessage(data.message || 'Face not recognized. Please try again.', 'error');
            setTimeout(() => {
                if (!recognizedUsername) detectFace();
            }, 2000);
        }
    } catch (error) {
        console.error('Error in face recognition:', error);
        updateMessage('Error processing facial image. Please try again.', 'error');
    }
}

// Record attendance (entry or exit) after successful face recognition
async function recordAttendance(type) {
    if (!recognizedUsername || !capturedImage) {
        updateMessage('Please wait for face recognition first.', 'error');
        return;
    }
    updateMessage(`Recording ${type} attendance...`, 'info');
    const formData = new FormData();
    formData.append("face_image", capturedImage);
    formData.append("attendance_type", type);
    try {
        const response = await fetch('/login/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrftoken
            }
        });
        const data = await response.json();
        if (data.status === 'success') {
            updateMessage(data.message || `Attendance successfully registered!`, 'success');
            if (data.redirect) {
                window.location.href = data.redirect;
            }
            setTimeout(() => {
                recognizedUsername = null;
                userInfo.style.display = 'none';
                startFaceDetection();
            }, 3000);
        } else {
            updateMessage(data.message || 'Failed to record attendance.', 'error');
        }
    } catch (error) {
        console.error('Error recording attendance:', error);
        updateMessage('An error occurred while recording attendance.', 'error');
    }
}

// Attach event listeners and start detection
document.addEventListener('DOMContentLoaded', () => {
    entryButton.addEventListener('click', () => recordAttendance('entry'));
    exitButton.addEventListener('click', () => recordAttendance('exit'));
    startFaceDetection();
});