FROM php:8.2-apache

WORKDIR /var/www/html

RUN a2enmod rewrite

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y gnupg2 libgssapi-krb5-2 curl apt-transport-https

# Eliminar paquetes ODBC conflictivos
RUN apt-get remove -y libodbc2 libodbccr2 libodbcinst2 unixodbc-common || true

# Instalar unixODBC y sus headers
RUN apt-get update && apt-get install -y unixodbc unixodbc-dev

# Instalar el repositorio de Microsoft y el ODBC Driver para SQL Server (para Debian 12/bookworm)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && echo "deb [arch=amd64] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Instalar extensiones de PHP para SQL Server
RUN pecl install sqlsrv pdo_sqlsrv \
    && docker-php-ext-enable sqlsrv pdo_sqlsrv

# Instalar Composer
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" \
    && php composer-setup.php --install-dir=/usr/local/bin --filename=composer \
    && php -r "unlink('composer-setup.php');"

COPY ./datos/composer.json .
COPY ./datos/.htaccess .

RUN apt-get update && apt-get install -y zip
RUN apt-get update && apt-get install -y git

RUN composer install

RUN composer dump-autoload

RUN sed -i 's/DocumentRoot.*$/DocumentRoot \/var\/www\/html\/public/' /etc/apache2/sites-enabled/000-default.conf