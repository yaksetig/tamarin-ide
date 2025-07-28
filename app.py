from flask import Flask, request, render_template_string, jsonify
import subprocess
import tempfile
import os
import json

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔍 Circomspect Web Interface</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container { 
            max-width: 1000px;
            margin: 0 auto;
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 { 
            font-size: 2.5rem; 
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p { 
            opacity: 0.9; 
            font-size: 1.1rem;
        }
        
        .content { padding: 40px; }
        
        .upload-area { 
            border: 3px dashed #3498db; 
            padding: 50px; 
            text-align: center; 
            margin: 30px 0; 
            border-radius: 15px;
            transition: all 0.3s ease;
            cursor: pointer;
            background: #f8f9fa;
        }
        
        .upload-area:hover { 
            border-color: #2980b9; 
            background: #e3f2fd;
            transform: translateY(-2px);
        }
        
        .upload-area.dragover { 
            border-color: #27ae60; 
            background: #e8f5e8;
            transform: scale(1.02);
        }
        
        .upload-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            color: #3498db;
        }
        
        textarea { 
            width: 100%; 
            height: 300px; 
            margin: 20px 0; 
            padding: 20px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
            transition: border-color 0.3s ease;
            background: #fafafa;
        }
        
        textarea:focus { 
            border-color: #3498db; 
            outline: none;
            background: white;
            box-shadow: 0 0 0 3px rgba(52,152,219,0.1);
        }
        
        .btn { 
            background: linear-gradient(135deg, #3498db, #2980b9); 
            color: white; 
            padding: 16px 40px; 
            border: none; 
            border-radius: 50px;
            cursor: pointer; 
            font-size: 18px;
            font-weight: 600;
            transition: all 0.3s ease;
            display: block;
            margin: 30px auto;
            box-shadow: 0 4px 15px rgba(52,152,219,0.3);
        }
        
        .btn:hover { 
            transform: translateY(-3px); 
            box-shadow: 0 8px 25px rgba(52,152,219,0.4);
        }
        
        .btn:disabled { 
            background: #bdc3c7; 
            cursor: not-allowed; 
            transform: none;
            box-shadow: none;
        }
        
        .result { 
            background: #f8f9fa; 
            padding: 25px; 
            margin: 25px 0; 
            border-left: 5px solid #3498db; 
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .error { 
            border-left-color: #e74c3c; 
            background: #fce4ec;
        }
        
        .success { 
            border-left-color: #27ae60; 
            background: #e8f5e8;
        }
        
        .warning { 
            border-left-color: #f39c12; 
            background: #fff3e0;
        }
        
        pre { 
            background: #2c3e50; 
            color: #ecf0f1; 
            padding: 20px; 
            border-radius: 10px; 
            overflow-x: auto;
            font-size: 14px;
            line-height: 1.5;
            margin: 15px 0;
            white-space: pre-wrap;
        }
        
        .loading { 
            text-align: center; 
            color: #3498db;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .file-info { 
            background: linear-gradient(135deg, #e3f2fd, #bbdefb); 
            padding: 15px; 
            border-radius: 10px; 
            margin: 15px 0;
            font-size: 14px;
            border-left: 4px solid #2196f3;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #7f8c8d;
            border-top: 1px solid #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Circomspect Web Interface</h1>
            <p>Security analysis for Circom circuits using circomspect</p>
        </div>
        
        <div class="content">
            <form id="uploadForm">
                <div class="upload-area" id="uploadArea">
                    <input type="file" id="fileInput" accept=".circom" style="display: none;">
                    <div class="upload-icon">📁</div>
                    <div>
                        <strong>Click to upload .circom file</strong><br>
                        <small style="color: #7f8c8d;">or drag & drop here</small>
                    </div>
                </div>
                
                <div id="fileInfo" class="file-info" style="display: none;"></div>
                
                <textarea 
                    id="codeArea" 
                    placeholder="Or paste your Circom code here..."
                ></textarea>
                
                <button type="submit" class="btn" id="auditBtn">
                    🔍 Run Circomspect Analysis
                </button>
            </form>
            
            <div id="results"></div>
        </div>
        
        <div class="footer">
            <p>Powered by <a href="https://github.com/trailofbits/circomspect" target="_blank">circomspect</a></p>
        </div>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const codeArea = document.getElementById('codeArea');
        const uploadForm = document.getElementById('uploadForm');
        const uploadArea = document.getElementById('uploadArea');
        const results = document.getElementById('results');
        const auditBtn = document.getElementById('auditBtn');
        const fileInfo = document.getElementById('fileInfo');

        // File upload handling
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        function handleFile(file) {
            if (!file.name.endsWith('.circom')) {
                alert('Please upload a .circom file');
                return;
            }
            
            fileInfo.style.display = 'block';
            fileInfo.innerHTML = `
                <strong>📄 ${file.name}</strong> 
                <span style="color: #666; margin-left: 10px;">${(file.size/1024).toFixed(1)} KB</span>
            `;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                codeArea.value = e.target.result;
            };
            reader.readAsText(file);
        }

        // Form submission
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const code = codeArea.value.trim();
            
            if (!code) {
                alert('Please provide Circom code to analyze');
                return;
            }

            auditBtn.disabled = true;
            auditBtn.innerHTML = '⏳ Running circomspect...';
            
            results.innerHTML = `
                <div class="result loading">
                    <h3>🔄 Running Circomspect Analysis...</h3>
                    <p>Please wait while we analyze your circuit</p>
                </div>
            `;

            try {
                const response = await fetch('/audit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({code: code})
                });
                
                const result = await response.json();
                displayResults(result);
                
            } catch (error) {
                results.innerHTML = `
                    <div class="result error">
                        <h3>❌ Network Error</h3>
                        <p>${error.message}</p>
                    </div>
                `;
            } finally {
                auditBtn.disabled = false;
                auditBtn.innerHTML = '🔍 Run Circomspect Analysis';
            }
        });
        
        function displayResults(result) {
            if (!result.success) {
                results.innerHTML = `
                    <div class="result error">
                        <h3>❌ Analysis Error</h3>
                        <pre>${result.error}</pre>
                    </div>
                `;
                return;
            }
            
            // Display the raw circomspect output
            if (result.output) {
                const hasIssues = result.output.includes('warning:') || 
                                 result.output.includes('error:') || 
                                 result.output.includes('advice:');
                
                results.innerHTML = `
                    <div class="result ${hasIssues ? 'warning' : 'success'}">
                        <h3>${hasIssues ? '📋 Analysis Results' : '✅ No Issues Found'}</h3>
                        ${hasIssues ? '<pre>' + result.output + '</pre>' : '<p>Circomspect found no issues in your circuit!</p>'}
                    </div>
                `;
            } else {
                results.innerHTML = `
                    <div class="result success">
                        <h3>✅ Analysis Complete</h3>
                        <p>Circomspect analysis completed successfully. No issues found.</p>
                    </div>
                `;
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/audit', methods=['POST'])
def audit():
    try:
        data = request.get_json()
        circom_code = data['code']
        
        # Create a temporary file for the circom code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.circom', delete=False) as f:
            f.write(circom_code)
            temp_file = f.name
        
        try:
            # Run circomspect
            result = subprocess.run(
                ['circomspect', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Return the output
            return jsonify({
                'success': True,
                'output': result.stdout if result.stdout else result.stderr,
                'returncode': result.returncode
            })
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Analysis timed out after 30 seconds'
        })
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'circomspect not found. Please ensure circomspect is installed and in PATH.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
