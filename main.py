from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf

app = FastAPI()

MODEL = tf.keras.models.load_model("./model.h5")

CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy"]

def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    return image

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Potato Disease Classifier</title>
        </head>
        <body>
            <h1>Potato Disease Classifier</h1>
            <form action="/predict" method="post" enctype="multipart/form-data" id="uploadForm">
                <input type="file" name="File" id="fileInput">
                <input type="submit" value="Predict" onclick="predict()">
            </form>
            <div id="result" style="margin-top: 20px;"></div>
            <img id="uploadedImage" style="display: none; max-width: 300px; margin-top: 20px;">
            <script>
                async function predict() {
                    const formData = new FormData();
                    const fileField = document.querySelector('input[type="file"]');
                    formData.append('File', fileField.files[0]);

                    const response = await fetch('/predict', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();
                    document.getElementById('result').innerHTML = `<p>Predicted Class: ${result.class}</p><p>Confidence: ${result.confidence}</p>`;
                    document.getElementById('uploadedImage').src = URL.createObjectURL(fileField.files[0]);
                    document.getElementById('uploadedImage').style.display = 'block';
                }
            </script>
        </body>
    </html>
    """

@app.post("/predict")
async def predict(
    File: UploadFile = File(...)
):
    image = read_file_as_image(await File.read())
    img_batch = np.expand_dims(image, 0) 

    predictions = MODEL.predict(img_batch)
    predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
    confidence = float(np.max(predictions[0]))

    return { 
        'class': predicted_class,
        'confidence': confidence
    }

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)