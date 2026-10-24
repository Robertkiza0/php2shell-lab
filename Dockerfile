ARG PHP_VERSION=8.3.36
FROM php:${PHP_VERSION}-apache

# Extensions WordPress needs
RUN docker-php-ext-install mysqli pdo_mysql

# Leave expose_php on so the version is visible in headers (useful for detection practice)
RUN printf "expose_php = On\nmemory_limit = 256M\n" > /usr/local/etc/php/conf.d/lab.ini

# Install WordPress
RUN curl -fsSL https://wordpress.org/latest.tar.gz -o /tmp/wp.tar.gz \
    && tar -xzf /tmp/wp.tar.gz -C /var/www/html --strip-components=1 \
    && rm /tmp/wp.tar.gz \
    && chown -R www-data:www-data /var/www/html

# Simple page that reports the exact PHP version (lab only, never on real servers)
RUN echo '<?php header("Content-Type: text/plain"); echo PHP_VERSION, "\n", PHP_SAPI, "\n";' \
    > /var/www/html/lab-version.php
