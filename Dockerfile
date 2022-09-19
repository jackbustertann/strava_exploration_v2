# installing python v3.8
FROM python:3.8-slim-buster

# setting working directory
WORKDIR /

# installing dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# add source code
COPY . .

# run python module
CMD [ "python3", "-m", "src"]
