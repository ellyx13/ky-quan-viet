docker run -d \
  --name kyquanviet-api \
  --restart always \
  -v $(pwd)/app/:/opt/projects/app/ \
  -v $(pwd)/logs/:/opt/projects/app/logs \
  -p 8011:8005 \
  --env-file ./.env/prod.env \
  --health-cmd "sh -c 'curl -s -f http://localhost:8005/v1/health/ping || exit 1'" \
  --health-interval 60s \
  --health-timeout 3s \
  --health-retries 3 \
  ellyx13/projects:kyquanviet-api \
  uvicorn main:app --reload --workers 2 --host 0.0.0.0 --port 8005
