if [ $# -gt 1 ]; then
        key=$2
else
        key="review"
fi

docker stop $key || echo "$key instance is not running"
docker rm $key || echo "no $key instance exist"
if [ $# -gt 0 ]; then
    docker stop $(docker ps -aq)
    docker rm $(docker ps -aq)
fi

docker build --tag $key:latest .

#docker-compose up --detach 

port=80
docker run  -p $port:$port -d \
       --name $key $key:latest 

docker logs $key

docker ps -a

