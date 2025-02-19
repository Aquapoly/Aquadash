from multiprocessing import cpu_count

# Socket Path
bind = 'unix:/var/run/gunicorn.sock'

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog =  '/home/aquapoly/Aquadash/Aquadash-backend/logs/access_log'
errorlog =  '/home/aquapoly/Aquadash/Aquadash-backend/logs/error_log'
