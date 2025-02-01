# Base Fluentd image (assicurati di utilizzare l'ultima versione stabile, se necessario)
FROM fluent/fluentd:edge

USER root

# Install dependencies, Fluentd, and plugins in a single layer
# Install required packages
RUN apk add --no-cache ruby ruby-dev build-base inotify-tools bash

# Install Fluentd and plugins
RUN gem install fluentd fluent-plugin-couch fluent-plugin-xml-parser fluent-plugin-parser fluent-plugin-xml

# Copy the configuration file
COPY etc/fluent.conf /fluentd/etc/fluent.conf

# Copy the monitoring script 
COPY scripts/filemonitoring_fluentd.sh /fluentd/scripts/filemonitoring_fluentd.sh

# Set permissions if needed
RUN chmod 644 /fluentd/etc/fluent.conf
RUN chmod +x /fluentd/scripts/filemonitoring_fluentd.sh

# Command to run Fluentd with custom config
#CMD ["fluentd", "-c", "/fluentd/etc/fluent.conf"]

# Command to run Fluentd with monitoring script 
CMD ["/bin/bash", "-c", "nohup /fluentd/scripts/filemonitoring_fluentd.sh & fluentd -c /fluentd/etc/fluent.conf"]