# 1. Base Image
    FROM python:3.11-slim
    
    # 2. Set working directory
    WORKDIR /app
    
    # 3. Copy requirements file
    COPY requirements.txt requirements.txt
    
    # 4. Install packages
    # This will now install google-generativeai
    RUN pip install --no-cache-dir -r requirements.txt
    
    # 5. Copy your application code
    COPY ./app /app/app
    
    # 6. Expose the port
    EXPOSE 8000
    
    # 7. The command to run your API
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]