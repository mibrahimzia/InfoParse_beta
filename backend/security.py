import re
import subprocess
from urllib.parse import urlparse
import logging

logger = logging.getLogger("webtapi.security")

def validate_url(url: str) -> bool:
    """Perform security checks on target URL"""
    try:
        # Basic URL validation
        if not re.match(r"^https?://", url):
            return False
        
        parsed = urlparse(url)
        
        # Block private/local networks
        if parsed.hostname in ["localhost", "127.0.0.1"]:
            return False
        if parsed.hostname and (
            parsed.hostname.startswith(("192.168.", "10.")) or 
            parsed.hostname.startswith("172.") and 16 <= int(parsed.hostname.split(".")[1]) <= 31
        ):
            return False
        
        # Check for common attack patterns
        if any(char in url for char in ["'", "\"", "<", ">", "\\", ".."]):
            return False
        
        # Run security scans (if tools available)
        try:
            # Check for disallowed paths
            gobuster = subprocess.run(
                ["gobuster", "dir", "-u", url, "-w", "common.txt", "-t", "5", "-r"],
                capture_output=True,
                timeout=10
            )
            if b"403" in gobuster.stdout or b"401" in gobuster.stdout:
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass  # Fail open if tools not available
        
        return True
        
    except Exception as e:
        logger.error(f"Security validation error: {str(e)}")
        return False