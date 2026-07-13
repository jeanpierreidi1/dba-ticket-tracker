\# 🎫 DBA Support Ticket Tracker



> \*\*A Python + PostgreSQL application that simulates a managed services DBA overnight support shift — logging client tickets by priority, tracking resolution time, documenting fixes, and generating an end-of-shift activity report.\*\*



\---



\## 📌 Project Overview



In a managed services DBA environment, every shift involves incoming client tickets that need to be prioritized, investigated, resolved, and documented. This project automates and simulates that complete workflow using Python and PostgreSQL — from the first ticket logged at 11:30 PM to the final handoff report at 8:00 AM.



```

Client reports issue

&#x20;       │

&#x20;       ▼

Ticket created \& prioritized (Critical → High → Medium → Low)

&#x20;       │

&#x20;       ▼

Status updated → "In Progress"

&#x20;       │

&#x20;       ▼

Issue investigated \& resolved

&#x20;       │

&#x20;       ▼

Resolution documented + time logged

&#x20;       │

&#x20;       ▼

End-of-shift report generated for incoming DBA team

```



\---



\## 🎯 Why This Project Exists



Managed services DBA teams like Fortified Data use ticketing systems to:



\- \*\*Prioritize\*\* incoming client issues so Critical problems are resolved first

\- \*\*Track time\*\* spent on each task for billing and accountability

\- \*\*Document\*\* resolution steps for knowledge sharing and audit trails

\- \*\*Generate\*\* shift handoff reports for the incoming team

\- \*\*Search\*\* historical tickets when a client calls about a recurring issue



This project demonstrates the complete DBA support workflow end-to-end — from ticket creation to shift report — using Python and a production-grade PostgreSQL database.



\---



\## 📁 Repository Structure



```

dba-ticket-tracker/

│

├── schema.sql              ← PostgreSQL table definition

├── ticket\_tracker.py       ← Main application (7 functions)

├── requirements.txt        ← Python dependencies

├── .env.example            ← Credential template

├── .gitignore              ← Excludes .env and cache files

└── README.md

```



\---



\## 🗄️ Database Schema



```sql

CREATE TABLE tickets (

&#x20;   ticket\_id       SERIAL          PRIMARY KEY,

&#x20;   client\_name     VARCHAR(100)    NOT NULL,

&#x20;   issue\_title     VARCHAR(200)    NOT NULL,

&#x20;   description     TEXT,

&#x20;   priority        VARCHAR(20)     DEFAULT 'Medium'

&#x20;                   CHECK (priority IN

&#x20;                       ('Critical','High','Medium','Low')),

&#x20;   status          VARCHAR(20)     DEFAULT 'Open'

&#x20;                   CHECK (status IN

&#x20;                       ('Open','In Progress','Resolved')),

&#x20;   assigned\_to     VARCHAR(100)    DEFAULT 'Jean Pierre Idi',

&#x20;   created\_at      TIMESTAMP       DEFAULT NOW(),

&#x20;   resolved\_at     TIMESTAMP,

&#x20;   time\_spent\_mins INTEGER         DEFAULT 0,

&#x20;   resolution      TEXT

);

```



\*\*Why PostgreSQL over SQLite?\*\*



| Feature | SQLite | PostgreSQL |

|---|---|---|

| CHECK constraints | Limited | ✅ Enforced at DB level |

| SERIAL auto-increment | Manual | ✅ Native |

| RETURNING clause | No | ✅ Returns inserted ID |

| ILIKE (case-insensitive search) | No | ✅ Native |

| Production-grade | No | ✅ Yes |

| Matches real managed services | No | ✅ Yes |



\---



\## ⚙️ Application Functions



| Function | What It Does |

|---|---|

| `create\_ticket()` | Logs a new client support ticket with priority |

| `update\_status()` | Moves ticket: Open → In Progress → Resolved |

| `resolve\_ticket()` | Documents resolution steps and logs time spent |

| `view\_open\_tickets()` | Shows shift queue sorted by priority |

| `view\_all\_tickets()` | Full ticket history including resolved |

| `search\_tickets()` | ILIKE keyword search across client, title, description |

| `generate\_shift\_report()` | End-of-shift KPI summary with client breakdown |



\---



\## 🌙 Simulated Overnight Shift



The main script simulates a complete DBA overnight shift:



| Time | Event | Resolution |

|---|---|---|

| 11:30 PM | Shift starts — 5 tickets logged | — |

| 11:45 PM | Critical: Acme connection timeout | Increased max\_connections 150→300 |

| 12:30 AM | High: Beta slow query (47 min) | Created index → 1m 52s |

| 1:30 AM | High: Gamma backup failure | Cleared 42GB, reran backup |

| 2:15 AM | High: Acme login latency (9s) | Index on last\_login → <1s |

| 3:00 AM | Queue check | 1 low-priority ticket remains |

| 8:00 AM | End-of-shift report generated | Handoff to incoming team |



\---



\## 📊 Sample Shift Report Output



```

============================================================

&#x20; DBA MANAGED SERVICES — SHIFT ACTIVITY REPORT

&#x20; Generated: 2026-07-13 08:00:00

============================================================



&#x20; 📊 SUMMARY

&#x20; Total tickets logged:          5

&#x20; Resolved this shift:           4

&#x20; Still open:                    1

&#x20; Resolution rate:               80.0%

&#x20; Total time logged:             180 mins (3h 0m)

&#x20; Avg resolution time:           45.0 mins



&#x20; 🚨 BY PRIORITY

&#x20;   Critical       1 tickets  █

&#x20;   High           3 tickets  ███

&#x20;   Low            1 tickets  █



&#x20; 🏢 BY CLIENT

&#x20; Client               Tickets    Resolved   Time (mins)

&#x20; ----------------------------------------------------

&#x20; Acme Corp            2          2          85

&#x20; Beta Ltd             1          1          60

&#x20; Gamma Inc            1          1          35

&#x20; Delta Corp           1          0          0



&#x20; ✅ KEY RESOLUTIONS THIS SHIFT



&#x20; Ticket #1 — Acme Corp \[Critical]

&#x20; Issue:      Database connection timeout on production

&#x20; Time spent: 45 mins

&#x20; Fix:        Increased max\_connections 150→300 in postgresql.conf.

&#x20;             Monitored 20 mins — stable.



&#x20; Ticket #2 — Beta Ltd \[High]

&#x20; Issue:      Monthly report query taking 45+ minutes

&#x20; Time spent: 60 mins

&#x20; Fix:        Created index on report\_date. Query: 47 mins → 1m 52s.



&#x20; Ticket #3 — Gamma Inc \[High]

&#x20; Issue:      Nightly backup job failed

&#x20; Time spent: 35 mins

&#x20; Fix:        Cleared 42GB old files. Reran backup — completed.

============================================================

```



\---



\## 🚀 How to Run



\### Prerequisites



| Tool | Version | Download |

|---|---|---|

| Python | 3.10+ | \[python.org](https://python.org) |

| PostgreSQL | 18.1 | \[postgresql.org](https://postgresql.org/download) |

| pgAdmin 4 | Latest | Included with PostgreSQL |



\### Step 1 — Clone the repository

```cmd

git clone https://github.com/jeanpierreidi1/dba-ticket-tracker.git

cd dba-ticket-tracker

```



\### Step 2 — Install dependencies

```cmd

pip install -r requirements.txt

```



\### Step 3 — Configure credentials

```cmd

copy .env.example .env

notepad .env

```



Add your PostgreSQL password:

```

DB\_HOST=localhost

DB\_PORT=5432

DB\_USER=postgres

DB\_PASSWORD=YourPasswordHere

DB\_NAME=dba\_tickets

```



\### Step 4 — Create the database in pgAdmin

1\. Open pgAdmin → connect to PostgreSQL

2\. Right-click \*\*postgres\*\* database → \*\*Query Tool\*\*

3\. Run: `CREATE DATABASE dba\_tickets;`

4\. Right-click \*\*dba\_tickets\*\* → \*\*Query Tool\*\*

5\. Paste and run `schema.sql`



\### Step 5 — Run the application

```cmd

python ticket\_tracker.py

```



\---



\## 🔍 Search Feature



The `search\_tickets()` function uses PostgreSQL's `ILIKE` for case-insensitive search across three columns simultaneously:



```python

search\_tickets("Acme")     # finds all Acme Corp tickets

search\_tickets("timeout")  # finds tickets mentioning timeout

search\_tickets("backup")   # finds backup-related tickets

```



```sql

WHERE client\_name  ILIKE %s

&#x20;  OR issue\_title  ILIKE %s

&#x20;  OR description  ILIKE %s

```



\---



\## 📋 Priority Queue Logic



Tickets are always displayed Critical-first using a CASE expression — ensuring the most urgent issues are always at the top of the DBA's queue:



```sql

ORDER BY

&#x20;   CASE priority

&#x20;       WHEN 'Critical' THEN 1

&#x20;       WHEN 'High'     THEN 2

&#x20;       WHEN 'Medium'   THEN 3

&#x20;       WHEN 'Low'      THEN 4

&#x20;   END,

&#x20;   created\_at ASC

```



\---



\## 🧰 Tech Stack



| Component | Technology |

|---|---|

| Language | Python 3.14 |

| Database | PostgreSQL 18.1 |

| DB Connector | psycopg2-binary |

| Config | python-dotenv (.env file) |

| IDE | VS Code |

| Version Control | Git / GitHub |

| OS | Windows 11 |



\---



\## 📋 Requirements



```

psycopg2-binary

python-dotenv

```



Install with:

```cmd

pip install -r requirements.txt

```



\---



\## 📈 Skills Demonstrated



\- Python application development with PostgreSQL integration via psycopg2

\- Relational database design with CHECK constraints for data integrity

\- DBA support workflow simulation — ticket lifecycle management

\- Priority-based queue management using SQL CASE expressions

\- Time tracking and shift reporting with aggregate SQL queries

\- Case-insensitive keyword search using PostgreSQL ILIKE

\- RETURNING clause for retrieving inserted record IDs

\- Secure credential management with python-dotenv (.env)

\- Git version control and GitHub repository management



\---



\## 🔒 Security Note



Never commit your `.env` file. The `.gitignore` file excludes it automatically. Always use `.env.example` as the template — add real credentials only in your local `.env` file.



\---



\## 👤 Author



\*\*Jean Pierre Idi\*\*

M.S. Business Informatics — Northern Kentucky University (2025)

📧 jeanpierreidi1@gmail.com | 🔗 github.com/jeanpierreidi1

