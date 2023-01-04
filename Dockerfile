FROM python:3
RUN mkdir -p /app/config; mkdir /app/cache
WORKDIR /app/
VOLUME /app/config
VOLUME /app/cache
VOLUME /var/log/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY config/* config/
COPY os_to_wled.py .

EXPOSE 8000

# Install python dependencies:
CMD ["python", "os_to_wled.py", "--server"]
