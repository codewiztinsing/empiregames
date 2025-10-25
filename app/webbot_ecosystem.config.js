module.exports = {
  apps: [
    {
      name: 'empire-webbot',
      script: 'webbot.py',
      interpreter: '/var/www/empiregames/app/venv/bin/python',
      cwd: '/var/www/empiregames/app',
      env_file: '/var/www/empiregames/app/config.env',
      
      // Logging
      log_file: '/var/www/empiregames/logs/webbot.log',
      out_file: '/var/www/empiregames/logs/webbot-out.log',
      error_file: '/var/www/empiregames/logs/webbot-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      
      // Restart policy
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: '10s',
      max_memory_restart: '500M',
      
      // Process management
      instances: 1,
      exec_mode: 'fork',
      
      // Environment variables
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: '/var/www/empiregames/app',
        DJANGO_SETTINGS_MODULE: 'core.settings'
      },
      
      // Monitoring
      watch: false,
      ignore_watch: ['node_modules', 'logs', '*.log', '__pycache__', '*.pyc'],
      
      // Advanced options
      kill_timeout: 5000,
      wait_ready: true,
      listen_timeout: 10000,
      
      // Health check
      health_check_grace_period: 3000,
      
      // Auto restart on file changes (disabled for production)
      watch_options: {
        usePolling: false,
        interval: 1000
      }
    }
  ],
  
  // Deployment configuration (optional)
  deploy: {
    production: {
      user: 'www-data',
      host: 'localhost',
      ref: 'origin/main',
      repo: 'git@github.com:your-repo/empiregames.git',
      path: '/var/www/empiregames',
      'post-deploy': 'cd app && ./run_webbot.sh restart'
    }
  }
};
