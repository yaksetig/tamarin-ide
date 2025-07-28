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
    <title>🔒 Tamarin Prover Web Interface</title>
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
        
        .mode-selector {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            justify-content: center;
        }
        
        .mode-btn {
            padding: 10px 20px;
            border: 2px solid #3498db;
            background: white;
            color: #3498db;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .mode-btn.active {
            background: #3498db;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Tamarin Prover Web Interface</h1>
            <p>Security protocol verification using Tamarin Prover</p>
        </div>
        
        <div class="content">
            <form id="uploadForm">
                <div class="mode-selector">
                    <button type="button" class="mode-btn active" id="checkMode">✓ Check Theory</button>
                    <button type="button" class="mode-btn" id="proveMode">🔍 Prove Lemmas</button>
                </div>
                
                <div class="upload-area" id="uploadArea">
                    <input type="file" id="fileInput" accept=".spthy" style="display: none;">
                    <div class="upload-icon">📁</div>
                    <div>
                        <strong>Click to upload .spthy file</strong><br>
                        <small style="color: #7f8c8d;">or drag & drop here</small>
                    </div>
                </div>
                
                <div id="fileInfo" class="file-info" style="display: none;"></div>
                
                <textarea 
                    id="codeArea" 
                    placeholder="Or paste your Tamarin theory code here..."
                ></textarea>
                
                <button type="submit" class="btn" id="processBtn">
                    🔒 Run Tamarin Analysis
                </button>
            </form>
            
            <div id="results"></div>
        </div>
        
        <div class="footer">
            <p>Powered by <a href="https://tamarin-prover.github.io/" target="_blank">Tamarin Prover</a></p>
        </div>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const codeArea = document.getElementById('codeArea');
        const uploadForm = document.getElementById('uploadForm');
        const uploadArea = document.getElementById('uploadArea');
        const results = document.getElementById('results');
        const processBtn = document.getElementById('processBtn');
        const fileInfo = document.getElementById('fileInfo');
        const checkMode = document.getElementById('checkMode');
        const proveMode = document.getElementById('proveMode');
        
        let currentMode = 'check';

        // Mode selection
        checkMode.addEventListener('click', () => {
            currentMode = 'check';
            checkMode.classList.add('active');
            proveMode.classList.remove('active');
            processBtn.innerHTML = '✓ Check Theory';
        });
        
        proveMode.addEventListener('click', () => {
            currentMode = 'prove';
            proveMode.classList.add('active');
            checkMode.classList.remove('active');
            processBtn.innerHTML = '🔍 Prove Lemmas';
        });

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
            if (!file.name.endsWith('.spthy')) {
                alert('Please upload a .spthy file');
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
                alert('Please provide Tamarin theory code to analyze');
                return;
            }

            processBtn.disabled = true;
            const originalText = processBtn.innerHTML;
            processBtn.innerHTML = '⏳ Processing...';
            
            results.innerHTML = `
                <div class="result loading">
                    <h3>🔄 Running Tamarin Analysis...</h3>
                    <p>Please wait while we ${currentMode === 'check' ? 'check your theory' : 'prove the lemmas'}</p>
                </div>
            `;

            try {
                const response = await fetch('/tamarin', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({code: code, mode: currentMode})
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
                processBtn.disabled = false;
                processBtn.innerHTML = originalText;
            }
        });
        
        function displayResults(result) {
            if (!result.success) {
                results.innerHTML = `
                    <div class="result error">
                        <h3>❌ Tamarin Error</h3>
                        <pre>${result.error}</pre>
                    </div>
                `;
                return;
            }
            
            // Display the raw tamarin output
            if (result.output) {
                const hasErrors = result.output.toLowerCase().includes('error') || 
                                 result.output.toLowerCase().includes('failed') ||
                                 result.returncode !== 0;
                
                const hasWarnings = result.output.toLowerCase().includes('warning');
                
                let resultClass = 'success';
                let resultIcon = '✅';
                let resultTitle = 'Analysis Complete';
                
                if (hasErrors) {
                    resultClass = 'error';
                    resultIcon = '❌';
                    resultTitle = 'Analysis Failed';
                } else if (hasWarnings) {
                    resultClass = 'warning';
                    resultIcon = '⚠️';
                    resultTitle = 'Analysis Complete with Warnings';
                }
                
                results.innerHTML = `
                    <div class="result ${resultClass}">
                        <h3>${resultIcon} ${resultTitle}</h3>
                        <pre>${result.output}</pre>
                    </div>
                `;
            } else {
                results.innerHTML = `
                    <div class="result success">
                        <h3>✅ Analysis Complete</h3>
                        <p>Tamarin analysis completed successfully.</p>
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

@app.route('/tamarin', methods=['POST'])
def tamarin_analysis():
    try:
        data = request.get_json()
        spthy_code = data['code']
        mode = data.get('mode', 'check')  # 'check' or 'prove'
        
        # Create a temporary file for the spthy code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.spthy', delete=False) as f:
            f.write(spthy_code)
            temp_file = f.name
        
        try:
            # Prepare tamarin command based on mode
            if mode == 'check':
                # Just check the theory syntax and wellformedness
                cmd = ['tamarin-prover', '--check-only', temp_file]
            else:  # prove mode
                # Attempt to prove all lemmas
                cmd = ['tamarin-prover', '--prove', temp_file]
            
            # Run tamarin-prover
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # Increased timeout for proof attempts
            )
            
            # Return the output
            return jsonify({
                'success': True,
                'output': result.stdout if result.stdout else result.stderr,
                'returncode': result.returncode,
                'mode': mode
            })
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Analysis timed out after 2 minutes'
        })
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'tamarin-prover not found. Please ensure Tamarin Prover is installed and in PATH.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/n8n/compile', methods=['POST'])
def n8n_compile():
    """
    N8N-compatible endpoint for compiling Tamarin theories.
    Expects JSON with 'code' field containing the .spthy code.
    Returns simple success/failure response.
    """
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            spthy_code = data.get('code', '')
        else:
            spthy_code = request.form.get('code', '')
        
        if not spthy_code:
            return jsonify({
                'success': False,
                'error': 'No code provided',
                'message': 'Please provide Tamarin theory code in the "code" field'
            }), 400
        
        # Create a temporary file for the spthy code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.spthy', delete=False) as f:
            f.write(spthy_code)
            temp_file = f.name
        
        try:
            # Run tamarin-prover with check-only flag
            result = subprocess.run(
                ['tamarin-prover', '--check-only', temp_file],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Determine if compilation was successful
            compilation_successful = result.returncode == 0
            
            # Prepare response
            response_data = {
                'success': compilation_successful,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'message': 'Compilation successful' if compilation_successful else 'Compilation failed'
            }
            
            # Return appropriate HTTP status
            status_code = 200 if compilation_successful else 400
            
            return jsonify(response_data), status_code
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Compilation timed out',
            'message': 'Tamarin compilation timed out after 60 seconds'
        }), 408
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'tamarin-prover not found',
            'message': 'Tamarin Prover is not installed or not in PATH'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Internal server error during compilation'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Quick check if tamarin-prover is available
        result = subprocess.run(['tamarin-prover', '--version'], 
                              capture_output=True, text=True, timeout=5)
        tamarin_available = result.returncode == 0
        
        return jsonify({
            'status': 'healthy',
            'tamarin_available': tamarin_available,
            'tamarin_version': result.stdout.strip() if tamarin_available else None
        })
    except:
        return jsonify({
            'status': 'healthy',
            'tamarin_available': False,
            'tamarin_version': None
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
