sleep 60

cd /app/rest_server
nohup /app/rest_server/rest_server > /tmp/rest_server.log &

cd /app/ftp_web_client
nohup /app/ftp_web_client/ftp_web_client > /tmp/ftp_web_client.log &

while true
do
  sleep 1
done
