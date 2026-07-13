# ticket_tracker.py
# DBA Support Ticket Tracker — Python + PostgreSQL
# Simulates a managed services DBA overnight support shift

import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# ── Load credentials from .env ────────────────────────────────────────────
load_dotenv()


# ── Database Connection ───────────────────────────────────────────────────
def get_connection():
    """
    Returns a PostgreSQL connection using credentials from .env
    In real managed services: connects to client database server
    """
    return psycopg2.connect(
        host     = os.getenv("DB_HOST",     "localhost"),
        port     = os.getenv("DB_PORT",     "5432"),
        user     = os.getenv("DB_USER",     "postgres"),
        password = os.getenv("DB_PASSWORD", ""),
        database = os.getenv("DB_NAME",     "dba_tickets")
    )


# ════════════════════════════════════════════════════════════════════
# FUNCTION 1: Create a New Ticket
# ════════════════════════════════════════════════════════════════════
def create_ticket(client, title, description, priority="Medium"):
    """
    Logs a new client support ticket into the database.

    Parameters:
        client      - client company name
        title       - short description of the issue
        description - detailed description
        priority    - Critical / High / Medium / Low
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tickets
            (client_name, issue_title, description, priority, status)
        VALUES (%s, %s, %s, %s, 'Open')
        RETURNING ticket_id, created_at
    """, (client, title, description, priority))

    result    = cursor.fetchone()
    ticket_id = result[0]
    created   = result[1].strftime('%Y-%m-%d %H:%M:%S')

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n{'='*50}")
    print(f"  🎫 TICKET #{ticket_id} CREATED")
    print(f"{'='*50}")
    print(f"  Client:      {client}")
    print(f"  Issue:       {title}")
    print(f"  Priority:    {priority}")
    print(f"  Created:     {created}")
    print(f"  Status:      Open")

    return ticket_id


# ════════════════════════════════════════════════════════════════════
# FUNCTION 2: Update Ticket Status
# ════════════════════════════════════════════════════════════════════
def update_status(ticket_id, new_status):
    """
    Updates the status of a ticket.
    Workflow: Open → In Progress → Resolved

    Parameters:
        ticket_id  - the ticket number to update
        new_status - 'Open', 'In Progress', or 'Resolved'
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tickets
        SET    status = %s
        WHERE  ticket_id = %s
        RETURNING client_name, issue_title
    """, (new_status, ticket_id))

    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if result:
        icon = {
            'Open':        '🔵',
            'In Progress': '🟡',
            'Resolved':    '✅'
        }.get(new_status, '⚪')

        print(f"\n  {icon} Ticket #{ticket_id} status → {new_status}")
        print(f"     {result[0]} — {result[1][:50]}")
    else:
        print(f"\n  ❌ Ticket #{ticket_id} not found")


# ════════════════════════════════════════════════════════════════════
# FUNCTION 3: Resolve a Ticket
# ════════════════════════════════════════════════════════════════════
def resolve_ticket(ticket_id, resolution, time_spent_mins):
    """
    Marks a ticket as Resolved.
    Documents exactly what was done and how long it took.
    This is what Fortified Data DBAs do at end of each ticket.

    Parameters:
        ticket_id       - ticket to resolve
        resolution      - detailed description of what was done
        time_spent_mins - how many minutes it took (for billing)
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tickets
        SET    status          = 'Resolved',
               resolved_at     = NOW(),
               time_spent_mins = %s,
               resolution      = %s
        WHERE  ticket_id = %s
        RETURNING client_name, issue_title, priority
    """, (time_spent_mins, resolution, ticket_id))

    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if result:
        print(f"\n{'='*50}")
        print(f"  ✅ TICKET #{ticket_id} RESOLVED")
        print(f"{'='*50}")
        print(f"  Client:      {result[0]}")
        print(f"  Issue:       {result[1][:50]}")
        print(f"  Priority:    {result[2]}")
        print(f"  Time logged: {time_spent_mins} minutes")
        print(f"  Fix:         {resolution[:80]}...")
    else:
        print(f"\n  ❌ Ticket #{ticket_id} not found")


# ════════════════════════════════════════════════════════════════════
# FUNCTION 4: View Open Tickets
# ════════════════════════════════════════════════════════════════════
def view_open_tickets():
    """
    Shows all open and in-progress tickets.
    Sorted by priority: Critical first, Low last.
    This is what a DBA checks at the start of each shift.
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ticket_id,
            client_name,
            issue_title,
            priority,
            status,
            created_at
        FROM tickets
        WHERE status IN ('Open', 'In Progress')
        ORDER BY
            CASE priority
                WHEN 'Critical' THEN 1
                WHEN 'High'     THEN 2
                WHEN 'Medium'   THEN 3
                WHEN 'Low'      THEN 4
            END,
            created_at ASC
    """)

    tickets = cursor.fetchall()
    cursor.close()
    conn.close()

    print(f"\n{'='*65}")
    print(f"  OPEN TICKETS — SHIFT QUEUE")
    print(f"{'='*65}")
    print(f"  {'#':<6} {'Priority':<10} {'Client':<18} {'Issue':<30}")
    print(f"  {'-'*62}")

    if not tickets:
        print(f"  ✅ Queue is clear — no open tickets!")
    else:
        for t in tickets:
            icon = {
                'Critical': '🔴',
                'High':     '🟠',
                'Medium':   '🟡',
                'Low':      '🟢'
            }.get(t[3], '⚪')

            print(f"  #{t[0]:<5} "
                  f"{icon} {t[3]:<8} "
                  f"{t[1]:<18} "
                  f"{t[2][:28]}")

    print(f"\n  Total open: {len(tickets)}")
    return tickets


# ════════════════════════════════════════════════════════════════════
# FUNCTION 5: View All Tickets
# ════════════════════════════════════════════════════════════════════
def view_all_tickets():
    """
    Shows complete ticket history including resolved tickets.
    Useful for generating shift handoff reports.
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ticket_id,
            client_name,
            issue_title,
            priority,
            status,
            time_spent_mins,
            created_at,
            resolved_at
        FROM tickets
        ORDER BY ticket_id
    """)

    tickets = cursor.fetchall()
    cursor.close()
    conn.close()

    print(f"\n{'='*70}")
    print(f"  ALL TICKETS — COMPLETE HISTORY")
    print(f"{'='*70}")
    print(f"  {'#':<5} {'Client':<18} {'Priority':<10} "
          f"{'Status':<14} {'Mins':<6} {'Issue'}")
    print(f"  {'-'*68}")

    for t in tickets:
        status_icon = {
            'Open':        '🔵',
            'In Progress': '🟡',
            'Resolved':    '✅'
        }.get(t[4], '⚪')

        print(f"  #{t[0]:<4} "
              f"{t[1]:<18} "
              f"{t[3]:<10} "
              f"{status_icon} {t[4]:<12} "
              f"{t[5]:<6} "
              f"{t[2][:25]}")

    print(f"\n  Total tickets: {len(tickets)}")
    return tickets


# ════════════════════════════════════════════════════════════════════
# FUNCTION 6: Search Tickets
# ════════════════════════════════════════════════════════════════════
def search_tickets(keyword):
    """
    Searches tickets by client name, issue title, or description.
    Useful when a client calls about a previous ticket.

    Parameters:
        keyword - text to search for
    """
    conn   = get_connection()
    cursor = conn.cursor()

    # %s wrapped in %% for LIKE pattern in psycopg2
    search_term = f"%{keyword}%"

    cursor.execute("""
        SELECT
            ticket_id,
            client_name,
            issue_title,
            priority,
            status
        FROM tickets
        WHERE client_name  ILIKE %s
           OR issue_title  ILIKE %s
           OR description  ILIKE %s
        ORDER BY created_at DESC
    """, (search_term, search_term, search_term))

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    print(f"\n  🔍 Search results for '{keyword}': "
          f"{len(results)} found")
    print(f"  {'-'*50}")

    for r in results:
        status_icon = {
            'Open':        '🔵',
            'In Progress': '🟡',
            'Resolved':    '✅'
        }.get(r[4], '⚪')
        print(f"  #{r[0]} [{r[3]}] {status_icon} {r[4]} "
              f"— {r[1]} — {r[2][:40]}")

    return results


# ════════════════════════════════════════════════════════════════════
# FUNCTION 7: Generate Shift Report
# ════════════════════════════════════════════════════════════════════
def generate_shift_report():
    """
    Generates a complete end-of-shift activity report.
    Shows all KPIs, client breakdown, and key resolutions.
    This is what you hand off to the incoming DBA team.
    """
    conn   = get_connection()
    cursor = conn.cursor()

    # ── Overall summary ───────────────────────────────────────────
    cursor.execute("""
        SELECT
            COUNT(*)                                        AS total,
            SUM(CASE WHEN status='Resolved' THEN 1 ELSE 0 END)
                                                            AS resolved,
            SUM(CASE WHEN status IN ('Open','In Progress')
                THEN 1 ELSE 0 END)                         AS still_open,
            COALESCE(SUM(time_spent_mins), 0)              AS total_mins,
            COALESCE(AVG(
                CASE WHEN status='Resolved'
                THEN time_spent_mins END), 0)              AS avg_mins
        FROM tickets
    """)
    summary = cursor.fetchone()

    total        = summary[0]
    resolved     = summary[1]
    still_open   = summary[2]
    total_mins   = summary[3]
    avg_mins     = round(summary[4], 1)
    success_rate = round(resolved / total * 100, 1) if total else 0

    # ── Priority breakdown ────────────────────────────────────────
    cursor.execute("""
        SELECT priority, COUNT(*) AS cnt
        FROM tickets
        GROUP BY priority
        ORDER BY
            CASE priority
                WHEN 'Critical' THEN 1
                WHEN 'High'     THEN 2
                WHEN 'Medium'   THEN 3
                WHEN 'Low'      THEN 4
            END
    """)
    by_priority = cursor.fetchall()

    # ── Client breakdown ──────────────────────────────────────────
    cursor.execute("""
        SELECT
            client_name,
            COUNT(*)                                    AS total,
            SUM(CASE WHEN status='Resolved'
                THEN 1 ELSE 0 END)                     AS resolved,
            COALESCE(SUM(time_spent_mins), 0)          AS total_mins
        FROM tickets
        GROUP BY client_name
        ORDER BY total DESC
    """)
    by_client = cursor.fetchall()

    # ── Key resolutions ───────────────────────────────────────────
    cursor.execute("""
        SELECT
            ticket_id,
            client_name,
            issue_title,
            priority,
            time_spent_mins,
            resolution
        FROM tickets
        WHERE status = 'Resolved'
          AND priority IN ('Critical', 'High')
        ORDER BY resolved_at DESC
        LIMIT 5
    """)
    key_resolutions = cursor.fetchall()

    cursor.close()
    conn.close()

    # ── Print the report ──────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  DBA MANAGED SERVICES — SHIFT ACTIVITY REPORT")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    print(f"\n  📊 SUMMARY")
    print(f"  {'Total tickets logged:':<30} {total}")
    print(f"  {'Resolved this shift:':<30} {resolved}")
    print(f"  {'Still open:':<30} {still_open}")
    print(f"  {'Resolution rate:':<30} {success_rate}%")
    print(f"  {'Total time logged:':<30} "
          f"{total_mins} mins "
          f"({total_mins//60}h {total_mins%60}m)")
    print(f"  {'Avg resolution time:':<30} {avg_mins} mins")

    print(f"\n  🚨 BY PRIORITY")
    for row in by_priority:
        bar = "█" * row[1]
        print(f"  {'  ' + row[0]:<14} {row[1]:>3} tickets  {bar}")

    print(f"\n  🏢 BY CLIENT")
    print(f"  {'Client':<20} {'Tickets':<10} "
          f"{'Resolved':<10} {'Time (mins)'}")
    print(f"  {'-'*52}")
    for row in by_client:
        print(f"  {row[0]:<20} {row[1]:<10} "
              f"{row[2]:<10} {row[3]}")

    if key_resolutions:
        print(f"\n  ✅ KEY RESOLUTIONS THIS SHIFT")
        for r in key_resolutions:
            print(f"\n  Ticket #{r[0]} — {r[1]} [{r[3]}]")
            print(f"  Issue:      {r[2]}")
            print(f"  Time spent: {r[4]} mins")
            if r[5]:
                print(f"  Fix:        {r[5][:100]}")

    print(f"\n{'='*60}")


# ════════════════════════════════════════════════════════════════════
# MAIN — Simulate a Full DBA Overnight Shift
# ════════════════════════════════════════════════════════════════════
if __name__ == "__main__":

    print("="*60)
    print("  DBA SUPPORT TICKET TRACKER")
    print("  Python + PostgreSQL")
    print(f"  Shift started: "
          f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # ── 11:30 PM: Shift starts — log incoming tickets ─────────────
    print("\n--- 11:30 PM: Shift starts — logging tickets ---")

    t1 = create_ticket(
        client      = "Acme Corp",
        title       = "Database connection timeout on production",
        description = "Users reporting connection timeouts on main "
                      "application database since 11 PM.",
        priority    = "Critical"
    )

    t2 = create_ticket(
        client      = "Beta Ltd",
        title       = "Monthly report query taking 45+ minutes",
        description = "Finance team says monthly summary query "
                      "is timing out. Was running in 3 mins last month.",
        priority    = "High"
    )

    t3 = create_ticket(
        client      = "Gamma Inc",
        title       = "Nightly backup job failed",
        description = "Automated backup at 10 PM did not complete. "
                      "Alert triggered at 10:47 PM.",
        priority    = "High"
    )

    t4 = create_ticket(
        client      = "Delta Corp",
        title       = "New read-only user account requested",
        description = "Auditor needs read-only access to "
                      "reporting schema by Monday.",
        priority    = "Low"
    )

    t5 = create_ticket(
        client      = "Acme Corp",
        title       = "Login page database latency",
        description = "Login taking 8-10 seconds since 10 PM deploy.",
        priority    = "High"
    )

    # ── View shift queue ──────────────────────────────────────────
    print("\n--- Shift queue ---")
    view_open_tickets()

    # ── Work through tickets ───────────────────────────────────────
    print("\n--- 11:45 PM: Starting Critical ticket ---")
    update_status(t1, "In Progress")

    resolve_ticket(
        ticket_id       = t1,
        resolution      = "Identified max_connections limit reached "
                          "(150/150). Increased to 300 in postgresql.conf, "
                          "reloaded config. Connections stabilized. "
                          "Monitored 20 mins — no recurrence. "
                          "Acme on-call notified at 12:15 AM.",
        time_spent_mins = 45
    )

    print("\n--- 12:30 AM: Working slow query ---")
    update_status(t2, "In Progress")

    resolve_ticket(
        ticket_id       = t2,
        resolution      = "EXPLAIN ANALYZE showed full table scan on "
                          "report_date column (2.1M rows). Created index: "
                          "CREATE INDEX idx_report_date ON monthly_summary"
                          "(report_date). Query time: 47 mins → 1m 52s. "
                          "Documented in change log. Beta team notified.",
        time_spent_mins = 60
    )

    print("\n--- 1:30 AM: Backup failure ---")
    update_status(t3, "In Progress")

    resolve_ticket(
        ticket_id       = t3,
        resolution      = "Backup drive at 98% capacity. Archived 42GB "
                          "of backup files older than 90 days to cold "
                          "storage. Drive now at 61%. Reran backup manually "
                          "— completed in 18 mins. Added disk space alert "
                          "at 80% threshold. Gamma team notified.",
        time_spent_mins = 35
    )

    print("\n--- 2:15 AM: Login latency ---")
    update_status(t5, "In Progress")

    resolve_ticket(
        ticket_id       = t5,
        resolution      = "Traced to user_sessions table — no index on "
                          "last_login column used in WHERE clause. Added "
                          "index: CREATE INDEX idx_last_login ON "
                          "user_sessions(last_login). Login: 9s → <1s. "
                          "Acme confirmed fix at 2:45 AM.",
        time_spent_mins = 40
    )

    # ── Check remaining queue ─────────────────────────────────────
    print("\n--- 3:00 AM: Checking remaining queue ---")
    view_open_tickets()

    # ── Search example ──────────────────────────────────────────
    print("\n--- Searching tickets for 'Acme' ---")
    search_tickets("Acme")

    # ── Full history ────────────────────────────────────────────
    print("\n--- Full ticket history ---")
    view_all_tickets()

    # ── End of shift report ───────────────────────────────────────
    print("\n--- 8:00 AM: End of shift report ---")
    generate_shift_report()

    print(f"\n✅ Shift complete — handoff report generated.")