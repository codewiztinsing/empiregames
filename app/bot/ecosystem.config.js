module.exports = {
  apps: [
    {
      name: 'empire-support-bot',
      script: 'support.py',
      interpreter: '/home/tinsae/Desktop/projects/empiregames/app/venv/bin/python',
      cwd: '/home/tinsae/Desktop/projects/empiregames/app/bot',
      env_file: '/home/tinsae/Desktop/projects/empiregames/app/bot/config.env',
      
      // Logging
      log_file: '/home/tinsae/Desktop/projects/empiregames/logs/support-bot.log',
      out_file: '/home/tinsae/Desktop/projects/empiregames/logs/support-bot-out.log',
      error_file: '/home/tinsae/Desktop/projects/empiregames/logs/support-bot-error.log',
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
        PYTHONPATH: '/home/tinsae/Desktop/projects/empiregames/app'
      },
      
      // Monitoring
      watch: false,
      ignore_watch: ['node_modules', 'logs', '*.log'],
      
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
      user: 'tinsae',
      host: 'localhost',
      ref: 'origin/main',
      repo: 'git@github.com:your-repo/empiregames.git',
      path: '/home/tinsae/Desktop/projects/empiregames',
      'post-deploy': 'cd app/bot && npm install && ./run_support_bot.sh restart'
    }
  }
};
