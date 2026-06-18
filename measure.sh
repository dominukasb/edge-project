#!/usr/bin/env bash
# Measure response time: local edge vs simulated remote (netem)

N=50
PAYLOAD='{"sensor_id":"temp-01","value":45,"timestamp":"2024-01-15T10:32:00Z"}'

measure() {
  url=$1
  for i in $(seq 1 $N); do
    curl -o /dev/null -s -w "%{time_total}\n" -X POST "$url" \
      -H "Content-Type: application/json" -d "$PAYLOAD"
  done | awk 'NR==1{min=max=$1}
              { sum+=$1; n++; if($1<min)min=$1; if($1>max)max=$1 }
              END { printf "avg=%.4fs  min=%.4fs  max=%.4fs", sum/n, min, max }'
}

echo "Requests per endpoint: $N"
echo ""
echo "Local  (edge):   $(measure http://127.0.0.1:8000/data)"
echo "Remote (netem):  $(measure http://127.0.0.1:8001/data)"
