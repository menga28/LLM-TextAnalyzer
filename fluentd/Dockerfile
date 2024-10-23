FROM fluent/fluentd:edge

USER root

# Install necessary dependencies and plugins
RUN apk update && \
    apk add --no-cache sudo build-base ruby-dev && \
    gem install fluent-plugin-elasticsearch fluent-plugin-mongo fluent-plugin-record-reformer

# Copy the configuration file
COPY fluent.conf /fluentd/etc/

CMD ["fluentd", "-c", "/fluentd/etc/fluent.conf"]
