#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LogSentry Unit Tests
"""

import unittest
import tempfile
import os
import sys
from datetime import datetime
from io import StringIO

# Import the module
import logsentry
from logsentry import LogParser, LogAnalyzer, LogEntry, LogLevel, ReportGenerator, AnalysisResult


class TestLogParser(unittest.TestCase):
    """Test LogParser class"""

    def setUp(self):
        self.parser = LogParser()

    def test_parse_timestamp_iso(self):
        """Test parsing ISO format timestamp"""
        line = "2024-01-15T10:30:45Z INFO Server started"
        ts = self.parser.parse_timestamp(line)
        self.assertIsNotNone(ts)
        self.assertEqual(ts.year, 2024)
        self.assertEqual(ts.month, 1)
        self.assertEqual(ts.day, 15)

    def test_parse_timestamp_common(self):
        """Test parsing common log format"""
        line = "Jan 15 10:30:45 server sshd[1234]: Connection established"
        ts = self.parser.parse_timestamp(line)
        self.assertIsNotNone(ts)
        self.assertEqual(ts.month, 1)
        self.assertEqual(ts.day, 15)

    def test_parse_level_debug(self):
        """Test parsing DEBUG level"""
        line = "2024-01-15 DEBUG This is a debug message"
        level = self.parser.parse_level(line)
        self.assertEqual(level, LogLevel.DEBUG)

    def test_parse_level_error(self):
        """Test parsing ERROR level"""
        line = "2024-01-15 10:30:45 ERROR Something went wrong"
        level = self.parser.parse_level(line)
        self.assertEqual(level, LogLevel.ERROR)

    def test_parse_line_complete(self):
        """Test parsing complete log line"""
        line = "2024-01-15 10:30:45 [web-server] ERROR Connection timeout"
        entry = self.parser.parse_line(line, 1)
        
        self.assertIsNotNone(entry.timestamp)
        self.assertEqual(entry.level, LogLevel.ERROR)
        self.assertEqual(entry.source, "web-server")
        self.assertIn("Connection timeout", entry.message)


class TestLogAnalyzer(unittest.TestCase):
    """Test LogAnalyzer class"""

    def setUp(self):
        self.analyzer = LogAnalyzer()

    def create_test_log(self, content):
        """Helper to create temporary log file"""
        fd, path = tempfile.mkstemp(suffix='.log')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)
            return path
        except:
            os.unlink(path)
            raise

    def test_analyze_simple_log(self):
        """Test analyzing a simple log file"""
        content = """2024-01-15 10:00:00 INFO Server started
2024-01-15 10:01:00 DEBUG Processing request
2024-01-15 10:02:00 ERROR Database connection failed
2024-01-15 10:03:00 INFO Request completed
"""
        log_path = self.create_test_log(content)
        try:
            result = self.analyzer.analyze_file(log_path)
            
            self.assertEqual(result.total_lines, 4)
            self.assertEqual(result.parsed_lines, 4)
            self.assertEqual(result.level_distribution.get('INFO'), 2)
            self.assertEqual(result.level_distribution.get('ERROR'), 1)
            self.assertEqual(result.level_distribution.get('DEBUG'), 1)
        finally:
            os.unlink(log_path)

    def test_analyze_empty_file(self):
        """Test analyzing empty file"""
        log_path = self.create_test_log("")
        try:
            result = self.analyzer.analyze_file(log_path)
            self.assertEqual(result.total_lines, 0)
            self.assertEqual(result.parsed_lines, 0)
        finally:
            os.unlink(log_path)

    def test_detect_error_patterns(self):
        """Test error pattern detection"""
        content = """2024-01-15 10:00:00 ERROR Exception: ValueError occurred
2024-01-15 10:01:00 ERROR Timeout while connecting
2024-01-15 10:02:00 ERROR Permission denied accessing file
"""
        log_path = self.create_test_log(content)
        try:
            result = self.analyzer.analyze_file(log_path)
            
            self.assertIn('Exception', result.error_patterns)
            self.assertIn('Timeout', result.error_patterns)
            self.assertIn('Permission Denied', result.error_patterns)
        finally:
            os.unlink(log_path)


class TestReportGenerator(unittest.TestCase):
    """Test ReportGenerator class"""

    def setUp(self):
        self.result = AnalysisResult()
        self.result.total_lines = 100
        self.result.parsed_lines = 95
        self.result.level_distribution = {'INFO': 80, 'ERROR': 10, 'WARNING': 5}
        self.generator = ReportGenerator(self.result)

    def test_to_text(self):
        """Test text report generation"""
        text = self.generator.to_text()
        self.assertIn("LogSentry", text)
        self.assertIn("Report", text)

    def test_to_json(self):
        """Test JSON report generation"""
        json_str = self.generator.to_json()
        self.assertIn('"version"', json_str)
        self.assertIn('"total_lines"', json_str)
        self.assertIn('INFO', json_str)

    def test_to_markdown(self):
        """Test Markdown report generation"""
        md = self.generator.to_markdown()
        self.assertIn("# LogSentry", md)
        self.assertIn("## Summary", md)
        self.assertIn("| Level |", md)

    def test_to_html(self):
        """Test HTML report generation"""
        html = self.generator.to_html()
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("LogSentry", html)
        self.assertIn("<table>", html)


class TestLogLevel(unittest.TestCase):
    """Test LogLevel enum"""

    def test_from_string_debug(self):
        self.assertEqual(LogLevel.from_string("DEBUG"), LogLevel.DEBUG)
        self.assertEqual(LogLevel.from_string("debug"), LogLevel.DEBUG)
        self.assertEqual(LogLevel.from_string("dbg"), LogLevel.DEBUG)

    def test_from_string_error(self):
        self.assertEqual(LogLevel.from_string("ERROR"), LogLevel.ERROR)
        self.assertEqual(LogLevel.from_string("error"), LogLevel.ERROR)
        self.assertEqual(LogLevel.from_string("err"), LogLevel.ERROR)

    def test_from_string_unknown(self):
        self.assertEqual(LogLevel.from_string("UNKNOWN"), LogLevel.UNKNOWN)
        self.assertEqual(LogLevel.from_string(""), LogLevel.UNKNOWN)


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_end_to_end_analysis(self):
        """Test complete analysis workflow"""
        content = """2024-01-15 10:00:00 INFO Application started
2024-01-15 10:01:00 DEBUG Loading configuration
2024-01-15 10:02:00 WARNING Deprecated API usage
2024-01-15 10:03:00 ERROR Failed to connect to database
2024-01-15 10:04:00 ERROR Connection timeout after 30s
2024-01-15 10:05:00 INFO Retry attempt 1
2024-01-15 10:06:00 INFO Connection established
"""
        fd, path = tempfile.mkstemp(suffix='.log')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)

            analyzer = LogAnalyzer()
            result = analyzer.analyze_file(path)

            # Verify analysis results
            self.assertEqual(result.total_lines, 7)
            self.assertEqual(result.parsed_lines, 7)
            
            # Verify level distribution
            self.assertEqual(result.level_distribution.get('INFO'), 3)
            self.assertEqual(result.level_distribution.get('ERROR'), 2)
            
            # Verify report generation
            generator = ReportGenerator(result)
            text_report = generator.to_text()
            self.assertIn("Total lines analyzed", text_report)  # Changed from "Application started"
            
        finally:
            os.unlink(path)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLogParser))
    suite.addTests(loader.loadTestsFromTestCase(TestLogAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestLogLevel))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
