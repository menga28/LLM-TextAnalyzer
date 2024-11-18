# Base Fluentd image (assicurati di utilizzare l'ultima versione stabile, se necessario)
FROM fluent/fluentd:edge

USER root

# Install dependencies, Fluentd, and plugins in a single layer
# Install required packages
RUN apk add --no-cache ruby ruby-dev build-base

# Install Fluentd and plugins
RUN gem install fluentd fluent-plugin-couch fluent-plugin-xml-parser fluent-plugin-parser fluent-plugin-xml

# Copy the configuration file
COPY etc/fluent.conf /fluentd/etc/fluent.conf

# Set permissions if needed
RUN chmod 644 /fluentd/etc/fluent.conf

# Command to run Fluentd with custom config
CMD ["fluentd", "-c", "/fluentd/etc/fluent.conf"]