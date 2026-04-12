"""
Main Flask application
Exposes REST API for code fixing
"""
from flask import Flask, request, jsonify
from pathlib import Path
import json
from loop_executor import LoopExecutor
from git_handler import GitHandler
from utils.logger import setup_logger

app = Flask(__name__)
logger = setup_logger(__name__)

# Initialize components
executor = LoopExecutor(use_ollama=False)  # Set to True if Ollama is available
git_handler = GitHandler()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'AI Bug Fixer API'}), 200

@app.route('/api/fix-file', methods=['POST'])
def fix_file():
    """
    Fix errors in a single file
    
    Request JSON:
    {
        "file_path": "/path/to/file.py",
        "language": "python",
        "max_attempts": 5,
        "timeout": 30
    }
    """
    try:
        data = request.get_json()
        
        file_path = Path(data.get('file_path'))
        language = data.get('language', 'python')
        max_attempts = data.get('max_attempts', 5)
        timeout = data.get('timeout', 30)
        
        if not file_path.exists():
            return jsonify({'error': f'File not found: {file_path}'}), 404
        
        logger.info(f"Fixing file: {file_path}")
        
        results = executor.execute_fix_loop(
            file_path=file_path,
            language=language,
            max_attempts=max_attempts,
            timeout=timeout
        )
        
        summary = executor.get_summary(results)
        
        return jsonify({
            'success': True,
            'file_path': str(file_path),
            'summary': summary,
            'iterations': [
                {
                    'attempt': r.iteration,
                    'success': r.success,
                    'exit_code': r.exit_code,
                    'errors_count': len(r.errors),
                    'errors': [
                        {'type': e.type, 'message': e.message}
                        for e in r.errors
                    ],
                    'stdout': r.stdout,
                    'stderr': r.stderr
                }
                for r in results
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fixing file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clone-repo', methods=['POST'])
def clone_repo():
    """
    Clone a Git repository
    
    Request JSON:
    {
        "repo_url": "https://github.com/user/repo.git",
        "repo_name": "optional-custom-name"
    }
    """
    try:
        data = request.get_json()
        
        repo_url = data.get('repo_url')
        repo_name = data.get('repo_name')
        
        if not repo_url:
            return jsonify({'error': 'repo_url is required'}), 400
        
        logger.info(f"Cloning repository: {repo_url}")
        
        repo_path = git_handler.clone_repository(repo_url, repo_name)
        
        return jsonify({
            'success': True,
            'repo_path': str(repo_path),
            'repo_url': repo_url
        }), 200
        
    except Exception as e:
        logger.error(f"Error cloning repository: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-file', methods=['GET'])
def get_file():
    """
    Get file content from repository
    
    Query parameters:
    - repo_path: Path to the repository
    - file_path: Relative path to file in repo
    """
    try:
        repo_path = request.args.get('repo_path')
        file_path = request.args.get('file_path')
        
        if not repo_path or not file_path:
            return jsonify({'error': 'repo_path and file_path are required'}), 400
        
        repo_path = Path(repo_path)
        content = git_handler.get_file_content(repo_path, file_path)
        
        return jsonify({
            'success': True,
            'file_path': file_path,
            'content': content
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-file', methods=['POST'])
def update_file():
    """
    Update file in repository
    
    Request JSON:
    {
        "repo_path": "/path/to/repo",
        "file_path": "relative/path/to/file.py",
        "content": "new file content"
    }
    """
    try:
        data = request.get_json()
        
        repo_path = Path(data.get('repo_path'))
        file_path = data.get('file_path')
        content = data.get('content')
        
        if not repo_path or not file_path or content is None:
            return jsonify({'error': 'repo_path, file_path, and content are required'}), 400
        
        git_handler.write_file_content(repo_path, file_path, content)
        
        return jsonify({
            'success': True,
            'file_path': file_path,
            'message': 'File updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/list-files', methods=['GET'])
def list_files():
    """
    List Python/JS/C++ files in repository
    
    Query parameters:
    - repo_path: Path to the repository
    - extensions: Comma-separated file extensions (e.g., '.py,.js,.cpp')
    """
    try:
        repo_path = request.args.get('repo_path')
        extensions = request.args.get('extensions', '.py,.js,.cpp').split(',')
        
        if not repo_path:
            return jsonify({'error': 'repo_path is required'}), 400
        
        repo_path = Path(repo_path)
        
        files = []
        for ext in extensions:
            files.extend(repo_path.rglob(f'*{ext.strip()}'))
        
        return jsonify({
            'success': True,
            'repo_path': str(repo_path),
            'files': [str(f.relative_to(repo_path)) for f in files]
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting AI Bug Fixer Backend...")
    app.run(debug=True, host='0.0.0.0', port=5000)
