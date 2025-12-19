#!/usr/bin/env python3
"""
Generate HTML report from k6 summary.json
"""
import json
import sys
from datetime import datetime

def format_duration(seconds):
    """Convert seconds to human-readable format"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        return f"{seconds/60:.2f}m"
    else:
        return f"{seconds/3600:.2f}h"

def format_bytes(bytes_val):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} TB"

def generate_html_report(summary_file, output_file):
    """Generate HTML report from k6 summary JSON"""
    try:
        with open(summary_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {summary_file} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {summary_file}")
        sys.exit(1)

    metrics = data.get('metrics', {})
    
    # Extract key metrics
    http_req_duration = metrics.get('http_req_duration', {})
    http_req_failed = metrics.get('http_req_failed', {})
    http_reqs = metrics.get('http_reqs', {})
    vus = metrics.get('vus', {})
    data_sent = metrics.get('data_sent', {})
    data_received = metrics.get('data_received', {})
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>k6 Load Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .timestamp {{
            color: #7f8c8d;
            margin-bottom: 30px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .metric-card.success {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .metric-card.warning {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        .metric-card.error {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }}
        .metric-label {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 8px;
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: bold;
        }}
        .metric-unit {{
            font-size: 14px;
            opacity: 0.8;
        }}
        h2 {{
            color: #2c3e50;
            margin: 30px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #ecf0f1;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            background: white;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        th {{
            background: #34495e;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .threshold-pass {{
            color: #27ae60;
            font-weight: bold;
        }}
        .threshold-fail {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .summary {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 k6 Load Test Report</h1>
        <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        
        <div class="summary">
            <h2>Test Summary</h2>
            <p><strong>Test Duration:</strong> {format_duration(data.get('root_group', {}).get('duration', 0) / 1000000000)}</p>
            <p><strong>Status:</strong> <span class="{'threshold-pass' if data.get('state', {}).get('testRunDurationMs', 0) > 0 else 'threshold-fail'}">{'Completed' if data.get('state', {}).get('testRunDurationMs', 0) > 0 else 'Failed'}</span></p>
        </div>

        <h2>Key Metrics</h2>
        <div class="metrics-grid">
            <div class="metric-card {'success' if http_req_failed.get('values', {}).get('rate', 0) < 0.05 else 'error'}">
                <div class="metric-label">HTTP Requests</div>
                <div class="metric-value">{http_reqs.get('values', {}).get('count', 0):,}</div>
                <div class="metric-unit">Total Requests</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Request Duration (p95)</div>
                <div class="metric-value">{http_req_duration.get('values', {}).get('p95', 0):.0f}</div>
                <div class="metric-unit">milliseconds</div>
            </div>
            
            <div class="metric-card {'success' if http_req_failed.get('values', {}).get('rate', 0) < 0.01 else 'warning' if http_req_failed.get('values', {}).get('rate', 0) < 0.05 else 'error'}">
                <div class="metric-label">Failed Requests</div>
                <div class="metric-value">{(http_req_failed.get('values', {}).get('rate', 0) * 100):.2f}%</div>
                <div class="metric-unit">{http_req_failed.get('values', {}).get('count', 0):,} failed</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Virtual Users</div>
                <div class="metric-value">{vus.get('values', {}).get('max', 0):,}</div>
                <div class="metric-unit">Peak VUs</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Data Sent</div>
                <div class="metric-value">{format_bytes(data_sent.get('values', {}).get('count', 0))}</div>
                <div class="metric-unit">Total</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Data Received</div>
                <div class="metric-value">{format_bytes(data_received.get('values', {}).get('count', 0))}</div>
                <div class="metric-unit">Total</div>
            </div>
        </div>

        <h2>Detailed Metrics</h2>
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Unit</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>HTTP Request Duration - Average</strong></td>
                    <td>{http_req_duration.get('values', {}).get('avg', 0):.2f}</td>
                    <td>ms</td>
                </tr>
                <tr>
                    <td><strong>HTTP Request Duration - Min</strong></td>
                    <td>{http_req_duration.get('values', {}).get('min', 0):.2f}</td>
                    <td>ms</td>
                </tr>
                <tr>
                    <td><strong>HTTP Request Duration - Max</strong></td>
                    <td>{http_req_duration.get('values', {}).get('max', 0):.2f}</td>
                    <td>ms</td>
                </tr>
                <tr>
                    <td><strong>HTTP Request Duration - p90</strong></td>
                    <td>{http_req_duration.get('values', {}).get('p90', 0):.2f}</td>
                    <td>ms</td>
                </tr>
                <tr>
                    <td><strong>HTTP Request Duration - p95</strong></td>
                    <td>{http_req_duration.get('values', {}).get('p95', 0):.2f}</td>
                    <td>ms</td>
                </tr>
                <tr>
                    <td><strong>HTTP Request Duration - p99</strong></td>
                    <td>{http_req_duration.get('values', {}).get('p99', 0):.2f}</td>
                    <td>ms</td>
                </tr>
                <tr>
                    <td><strong>HTTP Requests Rate</strong></td>
                    <td>{http_reqs.get('values', {}).get('rate', 0):.2f}</td>
                    <td>req/s</td>
                </tr>
                <tr>
                    <td><strong>HTTP Request Failed Rate</strong></td>
                    <td>{(http_req_failed.get('values', {}).get('rate', 0) * 100):.2f}%</td>
                    <td>percentage</td>
                </tr>
            </tbody>
        </table>

        <h2>Thresholds</h2>
        <table>
            <thead>
                <tr>
                    <th>Threshold</th>
                    <th>Status</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add threshold information if available
    thresholds = data.get('root_group', {}).get('thresholds', {})
    if thresholds:
        for threshold_name, threshold_data in thresholds.items():
            passed = threshold_data.get('ok', False)
            status_class = 'threshold-pass' if passed else 'threshold-fail'
            status_text = '✅ Passed' if passed else '❌ Failed'
            html += f"""
                <tr>
                    <td><strong>{threshold_name}</strong></td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{threshold_data.get('value', 'N/A')}</td>
                </tr>
"""
    else:
        html += """
                <tr>
                    <td colspan="3">No thresholds defined</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"HTML report generated successfully: {output_file}")

if __name__ == '__main__':
    summary_file = sys.argv[1] if len(sys.argv) > 1 else 'reports/summary.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'reports/k6-report.html'
    generate_html_report(summary_file, output_file)

