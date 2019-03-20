FROM mysql:5

COPY mysql-charset.cnf /etc/mysql/conf.d/mysql-charset.cnf

RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/*
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
