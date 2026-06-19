# Edge Node – Local Sensor Data Processing Service

A small web service that works as an **edge node**. It takes sensor readings at
`POST /data` and processes them right away on the same machine, instead of sending
them off to a far-away cloud server. For each reading it keeps a running average and
raises an alert if the value is too high. To show why processing locally is useful,
I also measured how long a request takes locally compared to a simulated slow
"cloud" connection.

> Built with help from AI (Claude) for writing code, explaining things, and fixing
> errors. I ran and checked everything myself.

## Machine specs

- **CPU:** Intel Core i5-10600KF @ 4.10GHz (6 cores / 12 threads)
- **RAM:** 32 GB
- **OS:** CachyOS (Arch-based), kernel 7.0.10
- **Docker:** 29.5.1 · **Python:** 3.14 (inside container)

## How to run

You need Docker and Docker Compose.

```
git clone https://github.com/dominukasb/edge-project.git
cd edge-project
docker compose up --build
```

This starts two services:
- `edge` – the local edge node at `http://127.0.0.1:8000`
- `remote` – the same service but with a 100 ms network delay, at `http://127.0.0.1:8001`

Send a reading:

```
curl -X POST http://127.0.0.1:8000/data -H "Content-Type: application/json" -d '{"sensor_id":"temp-01","value":45,"timestamp":"2026-06-18T12:54:00Z"}'
```

Run the timing test (50 requests to each):

```
bash measure.sh
```

## Results

Measured over 50 requests to each endpoint (see `results.txt`):

| Endpoint            | Avg      | Min      | Max      |
|---------------------|----------|----------|----------|
| Local (edge)        | 0.0010 s | 0.0009 s | 0.0012 s |
| Remote (100 ms)     | 0.2039 s | 0.2012 s | 0.3046 s |

The local service is about **200 times faster** than the simulated remote one.

The remote numbers come out around 200 ms even though I set the delay to 100 ms.
That's because one request actually travels back and forth a few times (first to
open the connection, then to send the data and get the answer), and the 100 ms delay
gets added each time.

What this test does **not** show: it only adds a fixed delay. A real cloud connection
would be less steady — the delay would change from request to request, some data
could get lost, and there would be extra work like encryption. So in real life the
difference would probably be even bigger and less predictable than these clean
numbers.

## Architecture

- **Language:** I used Python with FastAPI because it lets me build a small web
  service with very little code so I could understand everything better. It also checks
  the incoming data automatically.
- **What it does with the data:** it keeps a running average for each sensor and
  marks an alert when a value goes over 30. I only store the count and the total for
  each sensor, not every single reading, so it stays light on memory.
- **Containers:** there are two copies of the same service. One is the normal local
  edge node. The other is a "remote" copy where I added a 100 ms network delay using
  a Linux tool called `tc netem`, to act like a far-away cloud server.

## Retrospective

- Using `tc netem` to add a fake network delay was new to me.
- I was surprised the remote delay showed up as about 200 ms when I only set 100 ms.
  I learned this happens because each request goes back and forth more than once.
- The averages are only kept in memory, so they reset every time a container restarts.

## Next steps

- Save the sensor data somewhere (like a small database) so the averages don't reset
  on restart.
- Add some automatic tests.
