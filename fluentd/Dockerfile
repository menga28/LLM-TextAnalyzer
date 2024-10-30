FROM ruby:2.7-alpine

USER root

# Install necessary dependencies and plugins
RUN apk update && \
    apk add --no-cache build-base && \
    gem install fluent-plugin-arango fluent-plugin-xml

# Copy the configuration file
COPY etc/fluent.conf /fluentd/etc/

CMD ["fluentd", "-c", "/fluentd/etc/fluent.conf"]
