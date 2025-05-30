#!/bin/sh

# Start redis server
redis-server --protected-mode yes --bind $REDIS_IP --requirepass $REDIS_PASSWORD