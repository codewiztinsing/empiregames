module.exports = {
    apps: [
      {
        name: "celery-akbot",
        script: "/var/www/akerbingo/app/venv/bin/celery",
        args: "-A core worker -l info -c 4 -Q akbot_queue -n akbot@%h",
        interpreter: "none",
        cwd: "/var/www/akerbingo/app",
        env: {
          DJANGO_SETTINGS_MODULE: "core.settings",
        },
        user: "celery"
      }
    ]
  }
  