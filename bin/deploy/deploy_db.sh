docker ps -a --format '{{.Names}}' | grep -wq kyquanviet-db || docker run -d \
  --name kyquanviet-db \
  --restart always \
  -v $(pwd)/database:/data/db \
  -p 27021:27017 \
  --env-file ./.env/db.prod.env \
  --health-cmd "echo 'db.runCommand({serverStatus:1}).ok' | mongosh admin --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --quiet | grep 1" \
  --health-interval 60s \
  --health-timeout 60s \
  --health-retries 6 \
  mongo \
  --quiet
