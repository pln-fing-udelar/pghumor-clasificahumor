#!/usr/bin/env bash

for i in {1..10}; do
    curl -sS localhost:8000/tweets?a=$i > /dev/null &
done

wait
