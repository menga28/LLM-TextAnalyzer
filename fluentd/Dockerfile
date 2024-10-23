FROM fluent/fluentd:v1.12
USER root
RUN apk add --no-cache --update sudo build-base ruby-dev
RUN gem install fluent-plugin-elasticsearch fluent-plugin-mongo fluent-plugin-record-reformer
COPY fluent.conf /fluentd/etc/
CMD ["fluentd", "-c", "/fluentd/etc/fluent.conf"]
