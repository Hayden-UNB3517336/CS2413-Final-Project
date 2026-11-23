Worst-case exhaustive search time on ONE CPU core (estimated = keyspace x measured time per hash).

| Character set | Length | Entropy (bits) | SHA-256 (unsalted) | bcrypt (cost 12) | Argon2id (19 MiB, t=2) |
|---|---|---|---|---|---|
| digits (10) | 6 | 19.9 | < 1 second | 3.4 days | 7.0 hours |
| digits (10) | 8 | 26.6 | 1.4 minutes | 335.2 days | 29.1 days |
| digits (10) | 10 | 33.2 | 2.4 hours | 91.8 years | 8.0 years |
| digits (10) | 12 | 39.9 | 9.9 days | 9,177.5 years | 797.8 years |
| digits (10) | 14 | 46.5 | 2.7 years | 917,754.3 years | 79,782.0 years |
| lowercase (26) | 6 | 28.2 | 4.4 minutes | 2.8 years | 90.0 days |
| lowercase (26) | 8 | 37.6 | 2.1 days | 1,916.5 years | 166.6 years |
| lowercase (26) | 10 | 47.0 | 3.8 years | 1.3e+06 years | 112,626.0 years |
| lowercase (26) | 12 | 56.4 | 2,581.5 years | 8.8e+08 years | 7.6e+07 years |
| lowercase (26) | 14 | 65.8 | 1.7e+06 years | 5.9e+11 years | 5.1e+10 years |
| upper+lower (52) | 6 | 34.2 | 4.7 hours | 181.4 years | 15.8 years |
| upper+lower (52) | 8 | 45.6 | 1.4 years | 490,629.0 years | 42,651.3 years |
| upper+lower (52) | 10 | 57.0 | 3,910.5 years | 1.3e+09 years | 1.2e+08 years |
| upper+lower (52) | 12 | 68.4 | 1.1e+07 years | 3.6e+12 years | 3.1e+11 years |
| upper+lower (52) | 14 | 79.8 | 2.9e+10 years | 9.7e+15 years | 8.4e+14 years |
| alphanumeric (62) | 6 | 35.7 | 13.5 hours | 521.3 years | 45.3 years |
| alphanumeric (62) | 8 | 47.6 | 5.9 years | 2.0e+06 years | 174,196.2 years |
| alphanumeric (62) | 10 | 59.5 | 22,704.4 years | 7.7e+09 years | 6.7e+08 years |
| alphanumeric (62) | 12 | 71.5 | 8.7e+07 years | 3.0e+13 years | 2.6e+12 years |
| alphanumeric (62) | 14 | 83.4 | 3.4e+11 years | 1.1e+17 years | 9.9e+15 years |
| all printable (95) | 6 | 39.4 | 7.3 days | 6,746.3 years | 586.5 years |
| all printable (95) | 8 | 52.6 | 179.5 years | 6.1e+07 years | 5.3e+06 years |
| all printable (95) | 10 | 65.7 | 1.6e+06 years | 5.5e+11 years | 4.8e+10 years |
| all printable (95) | 12 | 78.8 | 1.5e+10 years | 5.0e+15 years | 4.3e+14 years |
| all printable (95) | 14 | 92.0 | 1.3e+14 years | 4.5e+19 years | 3.9e+18 years |
