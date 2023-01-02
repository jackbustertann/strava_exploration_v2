# installing python v3.9
FROM python:3.9-slim-buster

# setting working directory
WORKDIR /

# installing dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# add source code
COPY . .
ENV PORT 8080

# run python module
CMD [ "python3", "-m", "src"]
