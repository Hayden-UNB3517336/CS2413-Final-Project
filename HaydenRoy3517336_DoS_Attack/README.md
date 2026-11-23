Author: Hayden Roy
Mechanism: Network-level rate limiting against denial-of-service
Target: OWASP Juice Shop POST /rest/user/login, run locally on localhost:3000

*note: all tests were run against a local Juice Shop instance only. No external and/or third-party server was attacked.

To protect against DoS attacks, a per-IP rate limiter was added to the login route. 
This rate-limiter used the express-rate-limit package which was already implemented within Juice Shop.
To test the difference with and without an IP rate limiter, I gated the login route behind the DOS_PROTECTION environment variable.
This toggle is there for the express purpose of allowing me to control the measurements of both before or after on an identical build.

The protection was placed in an edited server.ts, at around line 635.

What this protection does is that when it receives requests exceeding 100/min from one IP, it will respond with HTTP (429 Too Many Requests) instead of processing the requests.

Experimental Setup
- Server: OWASP Juice Shop (Node.js/Typescript), on localhost:3000
- Load Generator: Locust 2.47.0, locustfile.py posting to /rest/user/login
- Machine: CPU = AMD RYZEN 5700x, RAM = 2*16GB, OS = Windows 11
- Locust config: wait_time = between(0, 0).
*note: The server was restarted before each "after" run to reset the rate-limit counter.

A copy of the attacker file is within this file, so to run the attack write the following:
```
python -m locust -f HaydenRoy3517336_DoS_Attack/locustfile.py --host http://localhost:3000
```
Then open localhost:8089, there you can set the user count/ramp per run.

To run the experiment for the "before" datasets, all that needs to be done is to set up the server in a separate command window with:
```
npm run build:server
npm start
```
To toggle the DoS protections on and then turn the server on, the following command should be run in the command window:
```
set DOS_PROTECTION=true
npm start
```
This will turn on the IP-based rate limit, making you able to make the "after" dataset. Between each load level, the server needs to be restarted after each test to ensure that the rate-limit counter can be properly reset.

The experiment was run at three load levels (10, 50, and 200 users), first without protection and then with the IP rate limiter enabled. The following datasets are what you should expect to find:

Before (no rate limiting):
| Users | Median (ms) | 95%ile (ms) | Max (ms) | RPS |
|-------|-------------|-------------|----------|-----|
| 10    | 120         | 140         | 171      | 81  |
| 50    | 590         | 640         | 696      | 83  |
| 200   | 2300        | 2500        | 2510     | 84  |

Without any protection, the server processes every request, and as the load increased, the median response time rose substantially from 120ms to 2300ms. All the while the throughput stayed flat at ~83 requests per second. This shows that without any protection, the server reaches a saturation point, where a regular users' login attempt, which usually would take a few milliseconds, could become unusably slow.

After:
| Users | Median (ms) | 95%ile (ms) | Max (ms) | RPS |
|-------|-------------|-------------|----------|-----|
| 10    | 25          | 33          | 6735     | 297 |
| 50    | 98          | 170         | 25642    | 249 |
| 200   | 450         | 1100        | 2481     | 297 |

With the protection on, requests over the 100/min limit were rejected with an instant HTTP 429 instead of being processed. This allowed the median response time to stay low (25-450ms) even at 200 users. Throughput also rose to around 250-297 requests per second. This is because the server can handle more requests per second because rejecting a request is far cheaper than processing a full login, and so the saturation point is never reached.

Comparison (median response time):
| Users | Before | After |
|-------|--------|-------|
| 10    | 120ms  | 25ms  |
| 50    | 590ms  | 98ms  |
| 200   | 2300ms | 450ms |

