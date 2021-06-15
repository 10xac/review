FROM python:3.6.13-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8501

RUN mkdir -p /root/.streamlit

RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'

RUN bash -c 'echo -e"\
[theme]\n\
base = \"light\"\n\
primaryColor = \"#ed1f33\"\n\
secondaryBackgroundColor = \"#ffffff\"\n\
textColor = \"#000000\"\n\
" > /root/.streamlit/config.toml'

CMD ["streamlit", "run", "reviewProd.py"]
