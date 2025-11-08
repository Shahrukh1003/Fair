"""
Database Manager for FairLens Fairness Monitoring System

Purpose: Manage SQLite database for temporal fairness drift tracking.
This module stores every fairness check result with timestamp, enabling
trend analysis and predictive drift detection.

How it fits: This is the PERSISTENCE layer in the FairLens pipeline.
Data → Metric → Detect → Alert → Log → [DB Storage] → Trend Analysis
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os


DB_PATH = os.path.join(os.path.dirname(__file__), 'fairness.db')


def init_database():
    """
    Initialize SQLite database with required tables.
    
    Tables:
    -------
    fairness_trends:
        - id: auto-increment primary key
        - timestamp: ISO format datetime
        - model_name: identifier for the AI model
        - dir_value: Disparate Impact Ratio
        - female_rate: approval rate for females
        - male_rate: approval rate for males
        - alert_status: boolean (True if DIR < 0.8)
        - drift_level: bias level used in simulation
        - n_samples: number of samples analyzed
        - hash_value: SHA256 hash for tamper-proof verification
        - explanation: text explanation of bias causes
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create fairness_trends table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fairness_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            model_name TEXT NOT NULL,
            dir_value REAL NOT NULL,
            female_rate REAL NOT NULL,
            male_rate REAL NOT NULL,
            alert_status INTEGER NOT NULL,
            drift_level REAL,
            n_samples INTEGER,
            hash_value TEXT UNIQUE,
            explanation TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create index on timestamp for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON fairness_trends(timestamp DESC)
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized: fairness.db")


def store_fairness_check(
    model_name: str,
    dir_value: float,
    female_rate: float,
    male_rate: float,
    alert_status: bool,
    drift_level: float = None,
    n_samples: int = None,
    hash_value: str = None,
    explanation: str = None
) -> int:
    """
    Store a fairness check result in the database.
    
    Parameters:
    -----------
    model_name : str
        Identifier for the AI model being monitored
    dir_value : float
        Disparate Impact Ratio value
    female_rate : float
        Approval rate for female applicants
    male_rate : float
        Approval rate for male applicants
    alert_status : bool
        True if DIR < 0.8 (bias detected)
    drift_level : float, optional
        Bias level used in simulation
    n_samples : int, optional
        Number of samples analyzed
    hash_value : str, optional
        SHA256 hash for verification
    explanation : str, optional
        Human-readable explanation of bias
    
    Returns:
    --------
    int : The ID of the inserted record
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO fairness_trends 
        (timestamp, model_name, dir_value, female_rate, male_rate, 
         alert_status, drift_level, n_samples, hash_value, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        timestamp,
        model_name,
        dir_value,
        female_rate,
        male_rate,
        1 if alert_status else 0,
        drift_level,
        n_samples,
        hash_value,
        explanation
    ))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return record_id


def get_recent_checks(limit: int = 10, model_name: str = None) -> List[Dict]:
    """
    Retrieve recent fairness checks from database.
    
    Parameters:
    -----------
    limit : int
        Number of recent records to retrieve
    model_name : str, optional
        Filter by specific model name
    
    Returns:
    --------
    List[Dict] : List of fairness check records
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if model_name:
        cursor.execute('''
            SELECT * FROM fairness_trends 
            WHERE model_name = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (model_name, limit))
    else:
        cursor.execute('''
            SELECT * FROM fairness_trends 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts
    results = []
    for row in rows:
        results.append({
            'id': row['id'],
            'timestamp': row['timestamp'],
            'model_name': row['model_name'],
            'dir_value': row['dir_value'],
            'female_rate': row['female_rate'],
            'male_rate': row['male_rate'],
            'alert_status': bool(row['alert_status']),
            'drift_level': row['drift_level'],
            'n_samples': row['n_samples'],
            'hash_value': row['hash_value'],
            'explanation': row['explanation']
        })
    
    return results


def get_record_by_id(record_id: int) -> Optional[Dict]:
    """
    Retrieve a specific fairness check record by ID.
    
    Parameters:
    -----------
    record_id : int
        The ID of the record to retrieve
    
    Returns:
    --------
    Dict or None : The record data or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM fairness_trends WHERE id = ?', (record_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row['id'],
            'timestamp': row['timestamp'],
            'model_name': row['model_name'],
            'dir_value': row['dir_value'],
            'female_rate': row['female_rate'],
            'male_rate': row['male_rate'],
            'alert_status': bool(row['alert_status']),
            'drift_level': row['drift_level'],
            'n_samples': row['n_samples'],
            'hash_value': row['hash_value'],
            'explanation': row['explanation']
        }
    
    return None


# Initialize database on module import
if not os.path.exists(DB_PATH):
    init_database()


"""
WHY THIS MATTERS FOR BANKING COMPLIANCE:

1. Temporal Tracking: Banks need to prove fairness over time, not just at one point.
   Regulators (RBI, EU AI Act) require continuous monitoring evidence.

2. Audit Trail: Every fairness check is permanently stored with timestamp.
   This creates an immutable history for regulatory review.

3. Trend Analysis: By storing historical data, we can detect gradual fairness
   degradation before it becomes a legal issue.

4. Tamper-Proof: Hash values ensure data integrity - no one can secretly
   modify past fairness results.

HOW TO EXTEND FOR PRODUCTION:
- Use PostgreSQL instead of SQLite for multi-user access
- Add data retention policies (e.g., keep 2 years of history)
- Implement database backups and replication
- Add indexes on model_name and alert_status for faster queries
"""
