#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LogSentry - Lightweight Log Intelligence Analysis Engine CLI
轻量级日志智能分析引擎 CLI 工具

A zero-dependency Python CLI tool for intelligent log analysis,
anomaly detection, and multi-format reporting.

Author: LogSentry Team
License: MIT
Version: 1.0.0
"""

import argparse
import json
import os
import re
import sys
import gzip
import bz2
import lzma
import sqlite3
import hashlib
import datetime
import threading
import time
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Iterator
from dataclasses import dataclass, field, asdict
from enum import Enum


__version__ = "1.0.0"
__author__ = "LogSentry Team"


class LogLevel(Enum):
    """Log severity levels"""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4
    UNKNOWN = 5

    @classmethod
    def from_string(cls, level_str: str) -> "LogLevel":
        """Parse log level from string"""
        level_map = {
            "debug": cls.DEBUG, "dbg": cls.DEBUG,
            "info": cls.INFO, "information": cls.INFO,
            "warn": cls.WARNING, "warning": cls.WARNING,
            "error": cls.ERROR, "err": cls.ERROR,
            "critical": cls.CRITICAL, "fatal": cls.CRITICAL, "crit": cls.CRITICAL,
        }
        return level_map.get(level_str.lower().strip(), cls.UNKNOWN)


@dataclass
class LogEntry:
    """Represents a single log entry"""
    timestamp: Optional[datetime.datetime] = None
    level: LogLevel = LogLevel.UNKNOWN
    source: str = ""
    message: str = ""
    raw_line: str = ""
    line_number: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Result of log analysis"""
    total_lines: int = 0
    parsed_lines: int = 0
    level_distribution: Dict[str, int] = field(default_factory=dict)
    time_range: Tuple[Optional[datetime.datetime], Optional[datetime.datetime]] = (None, None)
    top_errors: List[Tuple[str, int]] = field(default_factory=list)
    error_patterns: Dict[str, int] = field(default_factory=dict)
    source_distribution: Dict[str, int] = field(default_factory=dict)
    hourly_distribution: Dict[int, int] = field(default_factory=dict)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""


class LogParser:
    """Parse various log formats"""

    # Common timestamp patterns
    TIMESTAMP_PATTERNS = [
        # ISO 8601: 2024-01-15T10:30:45Z or 2024-01-15 10:30:45
        (r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)',
         '%Y-%m-%d %H:%M:%S'),
        # Common: Jan 15 10:30:45
        (r'([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', '%b %d %H:%M:%S'),
        # Common with year: Jan 15 2024 10:30:45
        (r'([A-Z][a-z]{2}\s+\d{1,2}\s+\d{4}\s+\d{2}:\d{2}:\d{2})', '%b %d %Y %H:%M:%S'),
        # Numeric: 15/01/2024 10:30:45
        (r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})', '%d/%m/%Y %H:%M:%S'),
        # Numeric US: 01/15/2024 10:30:45
        (r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})', '%m/%d/%Y %H:%M:%S'),
    ]

    # Log level patterns
    LEVEL_PATTERN = re.compile(
        r'\b(DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL|DBG|INF|ERR|CRIT)\b',
        re.IGNORECASE
    )

    def __init__(self):
        self.compiled_patterns = []
        for pattern, fmt in self.TIMESTAMP_PATTERNS:
            try:
                self.compiled_patterns.append((re.compile(pattern), fmt))
            except re.error:
                continue

    def parse_timestamp(self, line: str) -> Optional[datetime.datetime]:
        """Extract timestamp from log line"""
        for pattern, fmt in self.compiled_patterns:
            match = pattern.search(line)
            if match:
                try:
                    ts_str = match.group(1)
                    # Handle Z suffix
                    if ts_str.endswith('Z'):
                        ts_str = ts_str[:-1] + '+00:00'
                    # Handle T separator
                    if 'T' in ts_str:
                        ts_str = ts_str.replace('T', ' ')
                    # Remove timezone for parsing if present
                    if '+' in ts_str or ts_str.count('-') > 2:
                        # Try parsing with timezone
                        try:
                            return datetime.datetime.fromisoformat(ts_str.replace(' ', 'T'))
                        except ValueError:
                            pass
                    return datetime.datetime.strptime(ts_str, fmt)
                except (ValueError, IndexError):
                    continue
        return None

    def parse_level(self, line: str) -> LogLevel:
        """Extract log level from line"""
        match = self.LEVEL_PATTERN.search(line)
        if match:
            return LogLevel.from_string(match.group(1))
        return LogLevel.UNKNOWN

    def parse_line(self, line: str, line_number: int = 0) -> LogEntry:
        """Parse a single log line"""
        entry = LogEntry(
            raw_line=line,
            line_number=line_number
        )

        entry.timestamp = self.parse_timestamp(line)
        entry.level = self.parse_level(line)

        # Try to extract source/component
        source_match = re.search(r'\[([^\]]+)\]', line)
        if source_match:
            entry.source = source_match.group(1)

        # Extract message (after timestamp and level)
        message = line
        if entry.timestamp:
            # Remove timestamp from message
            for pattern, _ in self.compiled_patterns:
                message = pattern.sub('', message, count=1)
                break

        # Remove level indicators
        message = self.LEVEL_PATTERN.sub('', message, count=1)

        # Clean up
        message = re.sub(r'^\s*[-:]+\s*', '', message)
        entry.message = message.strip()

        return entry


class LogAnalyzer:
    """Analyze log entries and detect patterns"""

    # Common error patterns
    ERROR_PATTERNS = [
        (r'Exception[:\s]+(\w+)', 'Exception'),
        (r'Error[:\s]+(\w+)', 'Error'),
        (r'Failed to\s+(\w+)', 'Failed Action'),
        (r'Timeout', 'Timeout'),
        (r'Connection\s+(refused|reset|closed)', 'Connection Issue'),
        (r'Permission\s+denied', 'Permission Denied'),
        (r'No such file', 'File Not Found'),
        (r'MemoryError', 'Memory Error'),
        (r'Segmentation fault', 'Segmentation Fault'),
        (r'Stack trace', 'Stack Trace'),
    ]

    def __init__(self):
        self.parser = LogParser()
        self.compiled_error_patterns = [
            (re.compile(pattern, re.IGNORECASE), name)
            for pattern, name in self.ERROR_PATTERNS
        ]

    def analyze_file(self, file_path: str, progress_callback=None) -> AnalysisResult:
        """Analyze a log file"""
        result = AnalysisResult()
        entries: List[LogEntry] = []
        error_messages: List[str] = []

        # Detect file type and open accordingly
        opener = self._get_file_opener(file_path)

        try:
            with opener(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.rstrip('\n\r')
                    result.total_lines += 1

                    if progress_callback and line_num % 1000 == 0:
                        progress_callback(line_num)

                    if not line.strip():
                        continue

                    entry = self.parser.parse_line(line, line_num)
                    entries.append(entry)
                    result.parsed_lines += 1

                    # Track level distribution
                    level_name = entry.level.name
                    result.level_distribution[level_name] = result.level_distribution.get(level_name, 0) + 1

                    # Track source distribution
                    if entry.source:
                        result.source_distribution[entry.source] = result.source_distribution.get(entry.source, 0) + 1

                    # Track hourly distribution
                    if entry.timestamp:
                        hour = entry.timestamp.hour
                        result.hourly_distribution[hour] = result.hourly_distribution.get(hour, 0) + 1

                    # Track errors
                    if entry.level in (LogLevel.ERROR, LogLevel.CRITICAL):
                        error_messages.append(entry.message)
                        self._detect_error_patterns(entry.message, result.error_patterns)

        except Exception as e:
            print(f"Warning: Error reading file: {e}", file=sys.stderr)

        # Calculate time range
        timestamps = [e.timestamp for e in entries if e.timestamp]
        if timestamps:
            result.time_range = (min(timestamps), max(timestamps))

        # Find top errors
        error_counter = Counter(error_messages)
        result.top_errors = error_counter.most_common(10)

        # Detect anomalies
        result.anomalies = self._detect_anomalies(entries, result)

        # Generate summary
        result.summary = self._generate_summary(result)

        return result

    def _get_file_opener(self, file_path: str):
        """Get appropriate file opener based on extension"""
        if file_path.endswith('.gz'):
            return gzip.open
        elif file_path.endswith('.bz2'):
            return bz2.open
        elif file_path.endswith('.xz') or file_path.endswith('.lzma'):
            return lzma.open
        return open

    def _detect_error_patterns(self, message: str, patterns: Dict[str, int]):
        """Detect known error patterns in message"""
        for pattern, name in self.compiled_error_patterns:
            if pattern.search(message):
                patterns[name] = patterns.get(name, 0) + 1

    def _detect_anomalies(self, entries: List[LogEntry], result: AnalysisResult) -> List[Dict[str, Any]]:
        """Detect anomalies in log data"""
        anomalies = []

        # Check for error spikes
        if result.level_distribution.get('ERROR', 0) > result.parsed_lines * 0.1:
            anomalies.append({
                'type': 'error_spike',
                'severity': 'high',
                'description': f"High error rate: {result.level_distribution.get('ERROR', 0)} errors ({result.level_distribution.get('ERROR', 0) / max(result.parsed_lines, 1) * 100:.1f}%)",
            })

        # Check for time gaps
        timestamps = sorted([e.timestamp for e in entries if e.timestamp])
        if len(timestamps) > 1:
            time_span = timestamps[-1] - timestamps[0]
            expected_interval = time_span / max(len(timestamps), 1)

            for i in range(1, len(timestamps)):
                gap = timestamps[i] - timestamps[i-1]
                if gap > expected_interval * 10:
                    anomalies.append({
                        'type': 'time_gap',
                        'severity': 'medium',
                        'description': f"Unusual time gap: {gap} at {timestamps[i]}",
                    })
                    break  # Report first significant gap only

        # Check for burst patterns
        if result.hourly_distribution:
            max_hour = max(result.hourly_distribution.values())
            avg_hour = sum(result.hourly_distribution.values()) / len(result.hourly_distribution)
            if max_hour > avg_hour * 5:
                anomalies.append({
                    'type': 'traffic_burst',
                    'severity': 'medium',
                    'description': f"Traffic burst detected: {max_hour} events in peak hour vs {avg_hour:.0f} average",
                })

        return anomalies

    def _generate_summary(self, result: AnalysisResult) -> str:
        """Generate human-readable summary"""
        lines = []
        lines.append(f"Total lines analyzed: {result.total_lines}")
        lines.append(f"Successfully parsed: {result.parsed_lines}")

        if result.time_range[0] and result.time_range[1]:
            duration = result.time_range[1] - result.time_range[0]
            lines.append(f"Time range: {result.time_range[0]} to {result.time_range[1]} ({duration})")

        lines.append(f"\nLog level distribution:")
        for level, count in sorted(result.level_distribution.items(), key=lambda x: -x[1]):
            percentage = count / max(result.parsed_lines, 1) * 100
            lines.append(f"  {level}: {count} ({percentage:.1f}%)")

        if result.anomalies:
            lines.append(f"\n⚠️  Detected {len(result.anomalies)} anomaly/anomalies:")
            for anomaly in result.anomalies:
                icon = "🔴" if anomaly['severity'] == 'high' else "🟡"
                lines.append(f"  {icon} [{anomaly['type']}] {anomaly['description']}")

        return '\n'.join(lines)


class ReportGenerator:
    """Generate reports in various formats"""

    def __init__(self, result: AnalysisResult):
        self.result = result

    def to_text(self) -> str:
        """Generate plain text report"""
        lines = [
            "=" * 60,
            "LogSentry Analysis Report",
            "=" * 60,
            "",
            self.result.summary,
            "",
            "-" * 40,
            "Top Error Messages",
            "-" * 40,
        ]

        if self.result.top_errors:
            for msg, count in self.result.top_errors[:5]:
                lines.append(f"  ({count}x) {msg[:80]}...")
        else:
            lines.append("  No errors found")

        if self.result.error_patterns:
            lines.extend([
                "",
                "-" * 40,
                "Error Pattern Distribution",
                "-" * 40,
            ])
            for pattern, count in sorted(self.result.error_patterns.items(), key=lambda x: -x[1]):
                lines.append(f"  {pattern}: {count}")

        if self.result.source_distribution:
            lines.extend([
                "",
                "-" * 40,
                "Source Distribution",
                "-" * 40,
            ])
            for source, count in sorted(self.result.source_distribution.items(), key=lambda x: -x[1])[:10]:
                lines.append(f"  {source}: {count}")

        lines.extend([
            "",
            "=" * 60,
            f"Generated by LogSentry v{__version__}",
            "=" * 60,
        ])

        return '\n'.join(lines)

    def to_json(self) -> str:
        """Generate JSON report"""
        data = {
            'version': __version__,
            'generated_at': datetime.datetime.now().isoformat(),
            'analysis': {
                'total_lines': self.result.total_lines,
                'parsed_lines': self.result.parsed_lines,
                'level_distribution': self.result.level_distribution,
                'time_range': {
                    'start': self.result.time_range[0].isoformat() if self.result.time_range[0] else None,
                    'end': self.result.time_range[1].isoformat() if self.result.time_range[1] else None,
                },
                'top_errors': self.result.top_errors,
                'error_patterns': self.result.error_patterns,
                'source_distribution': self.result.source_distribution,
                'hourly_distribution': self.result.hourly_distribution,
                'anomalies': self.result.anomalies,
            }
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def to_markdown(self) -> str:
        """Generate Markdown report"""
        lines = [
            "# LogSentry Analysis Report",
            "",
            f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Version:** {__version__}",
            "",
            "## Summary",
            "",
            f"- **Total Lines:** {self.result.total_lines}",
            f"- **Parsed Lines:** {self.result.parsed_lines}",
        ]

        if self.result.time_range[0] and self.result.time_range[1]:
            lines.append(f"- **Time Range:** {self.result.time_range[0]} → {self.result.time_range[1]}")

        lines.extend([
            "",
            "## Log Level Distribution",
            "",
            "| Level | Count | Percentage |",
            "|-------|-------|------------|",
        ])

        for level, count in sorted(self.result.level_distribution.items(), key=lambda x: -x[1]):
            percentage = count / max(self.result.parsed_lines, 1) * 100
            lines.append(f"| {level} | {count} | {percentage:.1f}% |")

        if self.result.anomalies:
            lines.extend([
                "",
                "## ⚠️ Anomalies Detected",
                "",
            ])
            for anomaly in self.result.anomalies:
                severity_emoji = "🔴" if anomaly['severity'] == 'high' else "🟡"
                lines.append(f"- {severity_emoji} **{anomaly['type']}**: {anomaly['description']}")

        if self.result.top_errors:
            lines.extend([
                "",
                "## Top Error Messages",
                "",
                "| Count | Message |",
                "|-------|---------|",
            ])
            for msg, count in self.result.top_errors[:10]:
                escaped_msg = msg.replace('|', '\\|').replace('\n', ' ')[:60]
                lines.append(f"| {count} | {escaped_msg}... |")

        lines.extend([
            "",
            "---",
            f"*Generated by [LogSentry](https://github.com/gitstq/logsentry) v{__version__}*",
        ])

        return '\n'.join(lines)

    def to_html(self) -> str:
        """Generate HTML report"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LogSentry Analysis Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px 10px 0;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            color: #666;
            font-size: 0.9em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        .anomaly-high {{
            background: #fee;
            border-left: 4px solid #dc3545;
            padding: 10px;
            margin: 5px 0;
        }}
        .anomaly-medium {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px;
            margin: 5px 0;
        }}
        .level-debug {{ color: #6c757d; }}
        .level-info {{ color: #17a2b8; }}
        .level-warning {{ color: #ffc107; }}
        .level-error {{ color: #dc3545; }}
        .level-critical {{ color: #721c24; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ LogSentry Analysis Report</h1>
        <p>Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="card">
        <h2>📊 Overview</h2>
        <div class="metric">
            <div class="metric-value">{self.result.total_lines}</div>
            <div class="metric-label">Total Lines</div>
        </div>
        <div class="metric">
            <div class="metric-value">{self.result.parsed_lines}</div>
            <div class="metric-label">Parsed Lines</div>
        </div>
        <div class="metric">
            <div class="metric-value">{len(self.result.anomalies)}</div>
            <div class="metric-label">Anomalies</div>
        </div>
    </div>
"""

        if self.result.anomalies:
            html += """
    <div class="card">
        <h2>⚠️ Anomalies</h2>
"""
            for anomaly in self.result.anomalies:
                css_class = 'anomaly-high' if anomaly['severity'] == 'high' else 'anomaly-medium'
                html += f"""
        <div class="{css_class}">
            <strong>{anomaly['type']}</strong><br>
            {anomaly['description']}
        </div>
"""
            html += "    </div>\n"

        html += """
    <div class="card">
        <h2>📈 Log Level Distribution</h2>
        <table>
            <tr>
                <th>Level</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
"""
        for level, count in sorted(self.result.level_distribution.items(), key=lambda x: -x[1]):
            percentage = count / max(self.result.parsed_lines, 1) * 100
            level_class = f"level-{level.lower()}"
            html += f"""
            <tr>
                <td class="{level_class}">{level}</td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
            </tr>
"""

        html += """
        </table>
    </div>

    <div class="card">
        <p style="text-align: center; color: #666;">
            Generated by <a href="https://github.com/gitstq/logsentry">LogSentry</a> v""" + __version__ + """
        </p>
    </div>
</body>
</html>
"""
        return html


class RealTimeMonitor:
    """Monitor log files in real-time"""

    def __init__(self, analyzer: LogAnalyzer):
        self.analyzer = analyzer
        self.running = False
        self.stats = defaultdict(int)

    def monitor(self, file_path: str, callback=None):
        """Monitor a log file for new entries"""
        self.running = True

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Go to end of file
                f.seek(0, 2)

                print(f"🔍 Monitoring {file_path}... (Press Ctrl+C to stop)")

                while self.running:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue

                    line = line.rstrip('\n\r')
                    if not line.strip():
                        continue

                    entry = self.analyzer.parser.parse_line(line)
                    self.stats['total'] += 1
                    self.stats[entry.level.name] += 1

                    if callback:
                        callback(entry)
                    else:
                        self._default_callback(entry)

        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped")
        except Exception as e:
            print(f"Error: {e}")

    def _default_callback(self, entry: LogEntry):
        """Default callback for new log entries"""
        level_colors = {
            LogLevel.DEBUG: '\033[36m',      # Cyan
            LogLevel.INFO: '\033[32m',       # Green
            LogLevel.WARNING: '\033[33m',    # Yellow
            LogLevel.ERROR: '\033[31m',      # Red
            LogLevel.CRITICAL: '\033[35m',   # Magenta
            LogLevel.UNKNOWN: '\033[37m',    # White
        }
        reset = '\033[0m'

        color = level_colors.get(entry.level, '\033[37m')
        timestamp = entry.timestamp.strftime('%H:%M:%S') if entry.timestamp else '???:??:??'

        print(f"{color}[{timestamp}] [{entry.level.name:8}] {entry.message[:100]}{reset}")

        if entry.level in (LogLevel.ERROR, LogLevel.CRITICAL):
            print(f"   \033[91m⚠️  ERROR DETECTED\033[0m")

    def stop(self):
        """Stop monitoring"""
        self.running = False


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        prog='logsentry',
        description='LogSentry - Lightweight Log Intelligence Analysis Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze /var/log/syslog
  %(prog)s analyze app.log --format json --output report.json
  %(prog)s monitor /var/log/nginx/access.log
  %(prog)s analyze *.log --format html --output report.html
        """
    )

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze log files')
    analyze_parser.add_argument('files', nargs='+', help='Log files to analyze')
    analyze_parser.add_argument('-f', '--format', choices=['text', 'json', 'markdown', 'html'],
                               default='text', help='Output format')
    analyze_parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    analyze_parser.add_argument('--no-summary', action='store_true', help='Skip summary output')

    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor log files in real-time')
    monitor_parser.add_argument('file', help='Log file to monitor')
    monitor_parser.add_argument('--filter', help='Filter by log level')

    # Parse command (for testing)
    parse_parser = subparsers.add_parser('parse', help='Parse a single log line')
    parse_parser.add_argument('line', help='Log line to parse')

    return parser


def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    analyzer = LogAnalyzer()

    if args.command == 'analyze':
        all_results = []

        for file_path in args.files:
            if not os.path.exists(file_path):
                print(f"Error: File not found: {file_path}", file=sys.stderr)
                continue

            print(f"Analyzing {file_path}...", file=sys.stderr)
            result = analyzer.analyze_file(file_path)
            all_results.append((file_path, result))

        if not all_results:
            sys.exit(1)

        # Combine results if multiple files
        if len(all_results) == 1:
            combined_result = all_results[0][1]
        else:
            combined_result = AnalysisResult()
            for _, result in all_results:
                combined_result.total_lines += result.total_lines
                combined_result.parsed_lines += result.parsed_lines
                for level, count in result.level_distribution.items():
                    combined_result.level_distribution[level] = combined_result.level_distribution.get(level, 0) + count

        # Generate report
        generator = ReportGenerator(combined_result)

        if args.format == 'text':
            output = generator.to_text()
        elif args.format == 'json':
            output = generator.to_json()
        elif args.format == 'markdown':
            output = generator.to_markdown()
        elif args.format == 'html':
            output = generator.to_html()
        else:
            output = generator.to_text()

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Report saved to {args.output}")
        else:
            print(output)

    elif args.command == 'monitor':
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)

        monitor = RealTimeMonitor(analyzer)
        monitor.monitor(args.file)

    elif args.command == 'parse':
        entry = analyzer.parser.parse_line(args.line)
        print(f"Timestamp: {entry.timestamp}")
        print(f"Level: {entry.level.name}")
        print(f"Source: {entry.source}")
        print(f"Message: {entry.message}")


if __name__ == '__main__':
    main()
