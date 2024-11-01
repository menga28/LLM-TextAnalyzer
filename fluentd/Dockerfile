FROM fluent/fluentd:edge

USER root

# Install necessary dependencies and plugins
RUN apk update && \
    apk add --no-cache ruby-dev build-base && \
    gem install fluentd && \
    fluentd --setup /fluentd && \
    fluent-gem install fluent-plugin-arango fluent-plugin-xml

# Copy the configuration file
COPY etc/fluent.conf /fluentd/etc/

CMD ["fluentd", "-c", "/fluentd/etc/fluent.conf"]
