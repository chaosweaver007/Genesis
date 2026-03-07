# 🐛 Troubleshooting Guide

Common issues and solutions for Genesis Collective Consciousness Network.

## Quick Diagnostics

### Check System Status

```bash
# Check Python version
python --version

# Check if Flask is installed
python -c "import flask; print(flask.__version__)"

# Check if server is running
curl http://localhost:5003/ || echo "Server not responding"

# Check database connection
python -c "import sqlite3; print('SQLite OK')"
```

### Common Quick Fixes

1. **Restart the server**: Stop (`Ctrl+C`) and start again
2. **Clear browser cache**: Hard refresh (`Ctrl+Shift+R`)
3. **Check logs**: Look at console output or error logs
4. **Verify dependencies**: `pip install -r requirements.txt`
5. **Check file permissions**: Ensure Genesis folder is writable

## Installation Issues

### Python Version Error

**Problem**: "Python 3.11 or higher is required"

**Solution**:
```bash
# Check your Python version
python --version

# If too old, install Python 3.11+
# On Windows: Download from python.org
# On Mac: brew install python@3.11
# On Linux: sudo apt install python3.11
```

### Module Not Found

**Problem**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # Linux/Mac
# OR
.\.venv\Scripts\activate   # Windows

# Install dependencies
pip install flask flask-cors

# Or if requirements.txt exists
pip install -r requirements.txt
```

### Permission Denied

**Problem**: `PermissionError: [Errno 13] Permission denied`

**Solution**:
```bash
# On Linux/Mac, ensure proper permissions
chmod +x Genesis/*.py
chmod -R u+w Genesis/

# Check database directory permissions
ls -la /home/ubuntu/

# Create directory if needed
mkdir -p /home/ubuntu/synthsara_data
chmod -R u+w /home/ubuntu/synthsara_data
```

### Virtual Environment Issues

**Problem**: Cannot activate virtual environment

**Solution**:
```bash
# Delete and recreate
rm -rf .venv
python -m venv .venv

# Activate
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\activate   # Windows

# Reinstall dependencies
pip install flask flask-cors
```

## Server Issues

### Port Already in Use

**Problem**: `OSError: [Errno 98] Address already in use`

**Solution**:
```bash
# Find process using port 5003
# Linux/Mac:
lsof -i :5003
kill -9 <PID>

# Windows:
netstat -ano | findstr :5003
taskkill /PID <PID> /F

# Or change the port in collective_consciousness_home.py
# Change line: app.run(port=5004)  # Use different port
```

### Server Won't Start

**Problem**: Server starts but immediately exits

**Solution**:
1. Check for syntax errors in Python files
```bash
python -m py_compile Genesis/collective_consciousness_home.py
```

2. Check for import errors
```bash
cd Genesis
python -c "import collective_consciousness_home"
```

3. Review the error message and stack trace

4. Check file paths are correct

### Server Runs But Can't Access

**Problem**: Server running but http://localhost:5003 doesn't work

**Solution**:
```bash
# Check if server is listening
netstat -an | grep 5003

# Try 127.0.0.1 instead of localhost
http://127.0.0.1:5003

# Check firewall settings
# Windows: Allow Python through Windows Firewall
# Linux: sudo ufw allow 5003

# Check host binding in code
# Should be: app.run(host='0.0.0.0', port=5003)
```

### Slow Response Times

**Problem**: AI responses take too long

**Solution**:
1. Check system resources
```bash
# Linux/Mac
top
# Look for high CPU/memory usage

# Windows
taskmgr
```

2. Optimize database
```bash
# For SQLite
python -c "import sqlite3; conn = sqlite3.connect('collective_memory.db'); conn.execute('VACUUM'); conn.close()"
```

3. Clear old conversations
4. Restart server
5. Consider upgrading hardware

## Database Issues

### Database Locked

**Problem**: `sqlite3.OperationalError: database is locked`

**Solution**:
```bash
# Close all connections to database
# Stop the server
# Wait 30 seconds
# Restart

# If persists, check for stale lock
rm -f /home/ubuntu/collective_memory.db-journal

# Or switch to different database file
```

### Database Corrupted

**Problem**: `sqlite3.DatabaseError: database disk image is malformed`

**Solution**:
```bash
# Try to recover
sqlite3 collective_memory.db "PRAGMA integrity_check"

# If recovery fails, restore from backup
cp collective_memory.db.backup collective_memory.db

# Or start fresh (loses data!)
rm collective_memory.db
python memory_integration_system.py  # Recreate
```

### Cannot Create Database

**Problem**: Database file cannot be created

**Solution**:
```bash
# Check directory exists
mkdir -p /home/ubuntu/

# Check permissions
ls -la /home/ubuntu/
chmod u+w /home/ubuntu/

# Check disk space
df -h

# Try alternative location
# Edit config.py or collective_consciousness_home.py
# Change database path to writable location
```

## API Issues

### API Returns 404

**Problem**: API endpoint not found

**Solution**:
1. Check the endpoint URL is correct
2. Verify the server is running
3. Check Flask routes:
```python
python -c "from Genesis.collective_consciousness_home import app; print(app.url_map)"
```

### API Returns 500 Error

**Problem**: Internal server error

**Solution**:
1. Check server logs for error details
2. Verify request format is correct
3. Test with curl:
```bash
curl -X POST http://localhost:5003/api/steven/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"Hello"}'
```

### CORS Errors

**Problem**: "Access-Control-Allow-Origin" error in browser

**Solution**:
```python
# Ensure Flask-CORS is installed
pip install flask-cors

# Check CORS configuration in app
from flask_cors import CORS
CORS(app)
```

## AI Response Issues

### AI Not Responding

**Problem**: No response from Steven or Sarah

**Solution**:
1. Check server logs for errors
2. Verify AI implementation files exist
3. Test AI module directly:
```bash
cd Genesis
python -c "from steven_ai_implementation import StevenAI; ai = StevenAI(); print(ai.generate_response('Hello'))"
```

### Strange or Incorrect Responses

**Problem**: AI gives nonsensical or inappropriate responses

**Solution**:
1. Check training data integrity
2. Clear any cached responses
3. Restart the server
4. Report issue on GitHub with examples
5. Review ethical guidelines are being applied

### Persona Not Working

**Problem**: Steven/Sarah not responding in correct persona mode

**Solution**:
1. Verify persona mode is set correctly in request
2. Check persona implementation:
```python
# Check available personas
python -c "from Genesis.steven_ai_implementation import StevenAI; print(StevenAI().available_personas)"
```
3. Ensure persona mode is spelled correctly

## Memory System Issues

### Conversations Not Saving

**Problem**: Conversations not being archived

**Solution**:
1. Check consent level (Private doesn't save)
2. Verify database is writable
3. Check memory_integration_system.py:
```bash
python memory_integration_system.py
```
4. Review logs for save errors

### Pattern Extraction Failing

**Problem**: No patterns being extracted

**Solution**:
1. Check if conversations exist
2. Verify pattern extraction is enabled
3. Run manually:
```bash
python -c "from memory_integration_system import extract_patterns; extract_patterns()"
```
4. Check for threshold issues (need minimum conversations)

### Cannot Delete Data

**Problem**: Data deletion not working

**Solution**:
1. Verify user authentication
2. Check database permissions
3. Try direct database access:
```bash
sqlite3 collective_memory.db "DELETE FROM conversations WHERE user_id='your_id';"
```

## UI/Frontend Issues

### Page Not Loading

**Problem**: Web page doesn't display

**Solution**:
1. Check browser console for errors (F12)
2. Verify HTML template exists:
```bash
ls Genesis/templates/collective_home.html
```
3. Check Flask template rendering
4. Clear browser cache
5. Try different browser

### Styling Broken

**Problem**: CSS not loading, page looks unstyled

**Solution**:
1. Check CSS file exists:
```bash
ls Genesis/main.css
```
2. Verify CSS path in HTML template
3. Check Flask static file serving
4. Clear browser cache
5. Check browser developer console for 404 errors

### JavaScript Errors

**Problem**: Interactive features not working

**Solution**:
1. Open browser console (F12) → Console tab
2. Look for JavaScript errors
3. Check main.js exists and is loaded
4. Verify jQuery or other dependencies loaded
5. Check for conflicting scripts

### Mobile Display Issues

**Problem**: Site doesn't work on mobile

**Solution**:
1. Check viewport meta tag in HTML
2. Test responsive CSS
3. Verify touch events work
4. Check for mobile-specific errors in console
5. Test on multiple devices/browsers

## Performance Issues

### High CPU Usage

**Problem**: Genesis using too much CPU

**Solution**:
1. Check for infinite loops in logs
2. Optimize pattern extraction settings
3. Reduce batch sizes
4. Add delays between operations
5. Consider upgrading hardware

### High Memory Usage

**Problem**: Genesis consuming too much RAM

**Solution**:
1. Check for memory leaks
2. Limit conversation history size
3. Clear old conversations
4. Restart server regularly
5. Increase system RAM if needed

### Slow Pattern Extraction

**Problem**: Pattern extraction takes too long

**Solution**:
1. Process patterns in smaller batches
2. Add database indexes
3. Optimize extraction algorithms
4. Run extraction during off-peak hours
5. Consider async/background processing

## Network Issues

### Cannot Connect Remotely

**Problem**: Can't access Genesis from other devices

**Solution**:
```bash
# Ensure server binds to 0.0.0.0
# In collective_consciousness_home.py:
app.run(host='0.0.0.0', port=5003)

# Check firewall
sudo ufw allow 5003  # Linux
# Windows: Add inbound rule for port 5003

# Find your IP
ip addr show  # Linux
ipconfig      # Windows
```

### SSL/HTTPS Issues

**Problem**: Need secure connection but don't have SSL

**Solution**:
1. For development: Use ngrok or similar tunneling
```bash
ngrok http 5003
```

2. For production: Use Let's Encrypt
```bash
sudo certbot --nginx
```

3. Or use reverse proxy (nginx/Apache) with SSL

## Deployment Issues

### Docker Issues

**Problem**: Docker container won't start

**Solution**:
```bash
# Check Docker logs
docker logs genesis-container

# Rebuild image
docker build -t genesis .

# Check port mapping
docker ps -a

# Remove and recreate
docker rm genesis-container
docker run -p 5003:5003 genesis
```

### Cloud Deployment Issues

**Problem**: Can't deploy to cloud platform

**Solution**:
1. Check platform-specific logs
2. Verify environment variables set
3. Check port bindings
4. Review platform requirements
5. Ensure all dependencies listed
6. Check database connection strings

## Getting More Help

### Enable Debug Mode

For detailed error information:

```python
# In collective_consciousness_home.py
app.run(debug=True, host='0.0.0.0', port=5003)
```

⚠️ **Warning**: Never use debug mode in production!

### Collect Diagnostic Information

When reporting issues, include:

```bash
# System information
python --version
pip list
uname -a  # Linux/Mac
systeminfo  # Windows

# Genesis information
cd Genesis
git log -1
ls -la

# Error logs
tail -n 50 collective_server.err
```

### Report Issues

1. **Search existing issues**: [GitHub Issues](https://github.com/chaosweaver007/Genesis/issues)
2. **Create new issue** if not found
3. **Include**:
   - Clear problem description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Relevant logs
   - Screenshots if applicable

### Community Support

- **GitHub Discussions**: Q&A and general help
- **Discord**: Real-time community support
- **Email**: support@synthsara.org

### Emergency Contact

For critical security or ethical issues:

- **Security**: security@synthsara.org
- **Ethics**: ethics@synthsara.org

## Prevention Tips

### Regular Maintenance

```bash
# Weekly tasks
- Review logs for errors
- Check database size
- Clear old data if needed
- Update dependencies
- Backup database

# Monthly tasks
- Full system update
- Security review
- Performance optimization
- Backup verification
```

### Best Practices

1. **Keep Updated**: Regularly update Genesis and dependencies
2. **Monitor Logs**: Check logs periodically for warnings
3. **Backup Data**: Regular automated backups
4. **Test Changes**: Test in development before production
5. **Document Issues**: Keep notes on problems and solutions

---

**"Every problem is an invitation to deeper understanding. Every error is a teacher. Every challenge is an opportunity for growth."**

🔧 This troubleshooting guide is continuously updated. If you solve a problem not covered here, please contribute your solution!
