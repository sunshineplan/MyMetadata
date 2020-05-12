#! /bin/bash

installSoftware() {
    curl https://www.mongodb.org/static/pgp/server-4.2.asc | apt-key add -
    cat >>/etc/apt/sources.list.d/sunshine.list <<-EOF
		deb http://repo.mongodb.org/apt/debian $(lsb_release -sc)/mongodb-org/4.2 main
		EOF
    apt -qq update
    apt -qq -y install python3-flask python3-click python3-pymongo python3-pip uwsgi-plugin-python3 nginx git mongodb-org-tools
}

installMyMetadata() {
    mkdir -p /var/log/uwsgi
    pip3 install -e git+https://github.com/sunshineplan/MyMetadata.git#egg=metadata --src /var/www
    read -p 'Please enter mongo server address:' server
    read -p 'Please enter mongo server port:' port
    read -p 'Please enter database:' database
    read -p 'Please enter collection:' collection
    read -p 'Please enter username:' username
    read -sp 'Please enter password:' password
    echo
    cat >/var/www/metadata/metadata/config.py <<-EOF
		SERVER = '$server'
		PORT = $port
		DATABASE = '$database'
		COLLECTION = '$collection'
		USER = '$username'
		PASSWORD = '$password'
		EOF
}

setupMyMetadata() {
    read -p 'Please enter verify header:' header
    read -p 'Please enter verify header value:' value
    sed -i "s/\$domain/$domain/" /var/www/metadata/metadata/_api.py
    sed -i "s/\$header/$header/" /var/www/metadata/metadata/_api.py
    sed -i "s/\$value/$value/" /var/www/metadata/metadata/_api.py
}

setupsystemd() {
    cp -s /var/www/metadata/metadata.service /etc/systemd/system
    systemctl enable metadata
    service metadata start
}

writeLogrotateScrip() {
    if [ ! -f '/etc/logrotate.d/uwsgi' ]; then
        cat >/etc/logrotate.d/uwsgi <<-EOF
		/var/log/uwsgi/*.log {
		    copytruncate
		    rotate 12
		    compress
		    delaycompress
		    missingok
		    notifempty
		}
		EOF
    fi
}

createCronTask() {
    cp -s /var/www/metadata/BackupMyMetadata /etc/cron.monthly
    chmod +x /etc/cron.monthly/BackupMyMetadata
}

setupNGINX() {
    cp -s /var/www/metadata/MyMetadata.conf /etc/nginx/conf.d
    sed -i "s/\$domain/$domain/" /var/www/metadata/MyMetadata.conf
    service nginx reload
}

main() {
    read -p 'Please enter domain:' domain
    installSoftware
    installMyMetadata
    setupMyMetadata
    setupsystemd
    writeLogrotateScrip
    createCronTask
    setupNGINX
}

main
