# Base Fluentd image
FROM fluent/fluentd:edge

USER root

# Install dependencies, Fluentd, and plugins in a single layer
RUN apk update && \
    apk add --no-cache ruby-dev build-base && \
    gem install nokogiri fluentd fluent-plugin-couch fluent-plugin-xml && \
    fluentd --setup /fluentd && \
    apk del build-base ruby-dev

# Copy the configuration file
COPY etc/fluent.conf /fluentd/etc/fluent.conf

# Set permissions if needed
RUN chmod 644 /fluentd/etc/fluent.conf

# Command to run Fluentd with custom config
CMD ["fluentd", "-c", "/fluentd/etc/fluent.conf"]