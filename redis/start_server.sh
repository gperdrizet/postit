#!/bin/sh

# Set memory overcommit
sysctl vm.overcommit_memory=1

# Start redis server
redis-server \
--bind $REDIS_IP \
--requirepass $REDIS_PASSWORD