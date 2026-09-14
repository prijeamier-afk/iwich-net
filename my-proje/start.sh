#!/bin/sh
PORT=${PORT:-80}
rm -f /etc/nginx/sites-enabled/*
# تنظیم وب‌سرور برای تفکیک ترافیک پروکسی و پنل
cat <<EOF > /etc/nginx/conf.d/default.conf
server {
    listen ${PORT};

    location /ws-stream {
        proxy_redirect off;
        proxy_pass http://127.0.0.1:10001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$http_host;
    }

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# اجرای هسته شبکه در پس‌زمینه
/usr/local/bin/xray run -c /app/config.json &

# اجرای پنل مدیریتی پایتون
PORT=8081 python3 /app/main.py &

# اجرای وب‌سرور
nginx -g "daemon off;"
