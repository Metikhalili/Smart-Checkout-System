# Smart Checkout System

This project is a smart checkout application built with Python and Streamlit. It uses YOLOv8 to detect objects in images and webcam frames, count supported items, calculate their prices, and generate invoices.

I built this project to explore computer vision and how it can be used in a simple checkout system.

## Features

* Object detection using YOLOv8
* Real-time webcam processing
* Image upload and object detection
* Automatic item pricing and invoice calculation
* User registration and login
* Persian and English interface
* Invoice export to CSV
* Invoice history

## Technologies

* Python
* Streamlit
* Ultralytics YOLOv8
* OpenCV
* Pandas
* NumPy

## Installation

Clone the repository:

```bash
git clone https://github.com/Metikhalili/Smart-Checkout-System.git
cd Smart-Checkout-System
```

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install the required libraries:

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
streamlit run main.py
```

The application will open in your browser.

## How It Works

The application uses YOLOv8 to detect objects in uploaded images or webcam frames. Detected objects are matched against a predefined list of supported items, each with a fixed price.

The detected items are added to an invoice, and the total price is calculated automatically. Users can also add items manually and download invoice data as a CSV file.

## Notes

* The YOLOv8 model weights may be downloaded automatically on the first run.
* Only objects included in the pricing dictionary are used for invoice calculations.
* User information is stored in a local JSON file.
* The payment process is simulated and is not connected to a real payment gateway.
* This project is intended for learning and demonstration purposes, not production use.

## Future Improvements

* Improve object counting and tracking
* Add database support for users and invoices
* Improve authentication and password security
* Add a proper payment gateway integration
* Deploy the application online
