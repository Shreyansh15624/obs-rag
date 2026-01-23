# 1. Base Image: Use a lightweight Python 3.11 (Linux based)
FROM python:3.11-slim

# 2. Setup Work Directory: Just simply create a folder inside the container
WORKDIR /app

# 3. Optimization: Copying the requirements FIRST to use Docker Cache
# This makes re-building faster if we only change code, not libraries.
COPY requirements.txt .

# 4. Installing Dependencies
# --no-cache-dir helps keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the app code
COPY . .

# 6. Documentation: Telling Docker to post on port 8000, which is where we are listening
EXPOSE 8000

# 7. Start Command: Launch the FastAPI server
# --host 0.0.0.0 is MANDATORY for Docker to accept outside connections
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]