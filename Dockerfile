FROM python:3.6.13-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 80

RUN mkdir -p /root/.streamlit

RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'

RUN bash -c 'mv ./config.toml /root/.streamlit/config.toml'
RUN python3 gencred.py

ENTRYPOINT [ "streamlit", "run", "page.py", \
    "--server.port", "80", \
    "--server.enableCORS", "true", \
    "--browser.serverAddress", "0.0.0.0", \
    "--browser.serverPort", "443"]