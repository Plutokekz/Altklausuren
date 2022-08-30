FROM python:3.10-alpine
EXPOSE 80
RUN pip install --upgrade pip
WORKDIR /
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

CMD ["uvicorn", "main:app", "--proxy-headers" ,"--host", "0.0.0.0", "--port", "80"]