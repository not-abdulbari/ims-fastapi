
# Inventory Management System Backend

---
## ✅ Prerequisites

Before you start, make sure the following are installed:

- **Python 3.8 or later** – [Download here](https://www.python.org/downloads/)
- **pip** – Usually comes with Python. Check with `pip --version`
- **MySQL** – [Download here](https://dev.mysql.com/downloads/mysql/)

---

## Project Setup Guide

This document provides step-by-step instructions to set up and run the project on your local machine.

## 📥 Clone the repository

Run the following command to clone the repository:

```bash
git clone https://github.com/not-abdulbari/ims-fastapi
```
---

## 🐍 Set up the virtual environment

Activate the virtual environment to isolate the project dependencies.

### On Windows:

```bash
venv\Scripts\activate
```

### On macOS/Linux:

```bash
source venv/bin/activate
```

---

## 📦 Install dependencies

Use the following command to install all the required Python packages:

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the application

Start the development server using:

```bash
uvicorn main:app --reload
```

The `--reload` option will automatically restart the server when code changes are detected.

---

## 🌐 Access API documentation

After running the server, open the following URL in your browser to view and test the API documentation:

```
http://localhost:8000/docs
```

---

## ✅ Notes

* Make sure Python is installed before proceeding.
* Use `deactivate` in the terminal to exit the virtual environment after use.

---
