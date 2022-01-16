'use strict';

const { BasicTracerProvider, SimpleSpanProcessor } = require('@opentelemetry/tracing');
const { CollectorTraceExporter } =  require('@opentelemetry/exporter-collector');
const api = require('@opentelemetry/api');

class Tracer {
    constructor(appName, collectorHost) {
        const provider = new BasicTracerProvider()
        provider.register();
        provider.addSpanProcessor(
            new SimpleSpanProcessor(
                new CollectorTraceExporter({
                    serviceName: appName,
                    url: `http://${collectorHost}/v1/traces`
                })
            )
        );
    }

    startRootSpan(name) {
        const span = api.trace.getTracer().startSpan(name);
        const ctx = api.setSpan(api.context.active(), span);
        let carrier = {};
        api.propagation.inject(ctx, carrier);
        return { span: span, carriedCtx: carrier };
    }
    
    startChildSpan(name, carriedCtx) {
        const ctx = api.propagation.extract(api.context.active(), carriedCtx);
        const span = api.trace.getTracer().startSpan(name, undefined, ctx);
        const newCtx = api.setSpan(api.context.active(), span);
        let carrier = {};
        api.propagation.inject(newCtx, carrier);
        return { span: span, carriedCtx: carrier }
    }
}

module.exports = Tracer;