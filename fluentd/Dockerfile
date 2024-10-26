FROM fluent/fluentd:edge

USER root

# Install necessary dependencies and plugins
RUN apk update && \
    apk add --no-cache sudo build-base ruby-dev && \
    gem install fluent-plugin-elasticsearch fluent-plugin-mongo fluent-plugin-record-reformer fluent-plugin-xml nokogiri

# Copy the configuration file
COPY etc/fluent.conf /fluentd/etc/

CMD ["fluentd", "-c", "/fluentd/etc/fluent.conf"]
