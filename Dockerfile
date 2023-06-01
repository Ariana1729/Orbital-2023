FROM python:3.11

WORKDIR /app

COPY setup.py .
COPY vuln.py .
COPY requirements.txt .
COPY templates templates/

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["sh", "-c", "python setup.py && python vuln.py"]

