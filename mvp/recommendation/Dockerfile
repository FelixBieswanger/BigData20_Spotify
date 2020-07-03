#Base Image : Python
FROM python:3.7

#?
ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DontWarn

#Install Java 8
RUN set -e; \
    apt-get update; \
    apt-get install -y --no-install-recommends software-properties-common; \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0xB1998361219BD9C9; \
    apt-add-repository 'deb http://repos.azulsystems.com/debian stable main'; \
    apt-get update; \
    apt-get install -y --no-install-recommends zulu-8; \   
    apt-get clean; \
    rm -rf /var/tmp/* /tmp/* /var/lib/apt/lists/*


# Copy Directory into Docker
COPY . /

#Install python libraries
RUN set -e; pip install -r requirements.txt
CMD [ "python","Spark_RecEngine.py" ]