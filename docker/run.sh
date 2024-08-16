LOCAL_PATH=$(pwd)

docker run --rm -ti -e ORIGIN_HOST=pcef \
           -e ORIGIN_REALM=example.com \
           -e DESTINATION_HOST=pcrf \
           -e DESTINATION_REALM=example.com \
           -e DESTINATION_IP=127.0.0.1 \
           -e DESTINATION_PORT=3868 \
           -v $LOCAL_PATH/custom_handle_request.py:/app/custom_handle_request.py \
           diamtelecom:latest 