#!/bin/sh

# 替换环境变量
if [ -f /app/.env ]; then
  echo "Using .env file from volume"
else
  echo "Using default .env file"
  cp /app/.env.example /app/.env
fi

# 替换API URL
if [ -n "$API_URL" ]; then
  echo "Setting API_URL to $API_URL"
  sed -i "s|VUE_APP_API_URL=.*|VUE_APP_API_URL=$API_URL|g" /app/.env
fi

# 启动nginx
echo "Starting nginx..."
nginx -g 'daemon off;'
