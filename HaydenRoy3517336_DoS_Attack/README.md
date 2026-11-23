Author: Hayden Roy
Mechanism: Network-level rate limiting against denial-of-service
Target OWASP Juice Shop POST /rest/user/login, run locally on localhost:3000

*note: all tests were run against a local Juice Shop instance only. No external and/or third-party server was attacked.

To protect against DoS attacks, a per-IP rate limiter was added to the login route. 
This rate-limiter used the express-rate-limit package which was already implemented within Juice Shop.
To test the difference with and without an IP rate limiter, I gated the the login route behind the DOS_PROTECTION environment variable.
This toggle is there for the express purpose of allowing to control the measurements of both before or after on an identical build.

The protection was placed in an edited server.ts, at around line 635.

What this protection does is that when it receives requests exceeding 100/min from one IP, it will receive HTTP (429 Too Many Requests) instead of processing the requests.

Experimental Setup
- Server: OWASP Juice Shop (Node.js/Typescript), on localhost:3000
- Load Generator: Locust 2.47.0, locustfile.py posting to /rest/user/login
- Machine: CPU = AMD RYZEN 5700x, RAM = 2*16GB, OS = Windows 11
- Locust config: wait_time = between(0, 0).
*note: The server was restarted before each "after" run to reset the rate-limit counter.

A copy of the attacker file is within this file, so to run the attack right the following:
```
python -m locust -f HaydenRoy3517336_DoS_Attack/locustfile.py --host http://localhost:3000
```
Then open localhost:8089, there you can set the user count/ramp per run.

To run the experiment for the before datasets, all the that needs to be done is to set up the server with:
```
npm run build:server
npm start
```


