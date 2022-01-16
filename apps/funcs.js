'use strict';

async function invoke(nextFn, params) {	
	delete params['duration'];
	delete params['alpha'];
	delete params['beta'];
	const ow = require('openwhisk')({
		apihost: params.owHost,
		api_key: params.owAuth,
		ignore_certs: true
	});
	if (nextFn.length > 1) {
		for (let i = 0; i < nextFn.length; i++) {
			ow.actions.invoke({ actionName: `${params.appName}-dev-${nextFn[i]}`, params, blocking: false });
			if (i < (nextFn.length - 1)) {
				await timeout(15);
			}
		}
	} else {
		ow.actions.invoke({ actionName: `${params.appName}-dev-${nextFn}`, params, blocking: false });
	}
}

function getNextFunctions(functionName, functionGraph, missingFunctionAnomalies) {
	let nextFn = functionGraph[functionName];
	if (missingFunctionAnomalies.length == 0) {
		return nextFn;
	} 
	let newNextFn = new Array();
	for (let i = 0; i < nextFn.length; i++) {
		if (missingFunctionAnomalies.includes(nextFn[i])) {
			// Function nextFn[i] will be skipped. If nextFn[i] has successor functions, these are to be called directly.
			if (functionGraph[nextFn[i]] != 'None') {
				newNextFn = newNextFn.concat(getNextFunctions(nextFn[i], functionGraph, missingFunctionAnomalies));
			}
		} else {
			// Function nextFn[i] won't be skipped.
			newNextFn.push(nextFn[i]);
		}
	}
	return newNextFn;
}

async function main(params) {
	console.log(params)
	const Tracer = require('./tracing.js');
	const tracer = new Tracer(params.appName, params.collectorHost);
	const { span, carriedCtx } = tracer.startRootSpan(process.env.__OW_ACTION_NAME);
	params['carriedCtx'] = carriedCtx;
	span.setAttributes({
		activationId: process.env.__OW_ACTIVATION_ID,
		sampleId: params.sampleId,
		random: params.random
	});
	if (params.functionGraph['main'] != 'None') {
		const nextFn = getNextFunctions('main', params.functionGraph, params.missingFunctionAnomalies);
		await invoke(nextFn, params);
	}
	span.end();
}

function timeout(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

async function f(params) {
	console.log(params);
	const dist = require('probability-distributions');
	const Tracer = require('./tracing.js');
	const tracer = new Tracer(params.appName, params.collectorHost);
	const { span, _ } = tracer.startChildSpan(process.env.__OW_ACTION_NAME, params.carriedCtx);
	span.setAttributes({
		activationId: process.env.__OW_ACTIVATION_ID
	});
	
	let duration;
	const functionName = process.env.__OW_ACTION_NAME.split('-').slice(-1)[0];
	if (params.executionAnomalies.includes(functionName)) {
		// Function duration is an anomaly.
		if (Math.random() > 0.5) {
			// Abnormal long function execution.
			duration = 100;
		} else {
			// Abnormal short function execution.
			duration = 5;
		}
	} else {
		// Function duration is not an anomaly.
		if (params.random) {
			duration = dist.rgamma(1, params.alpha, params.beta)[0];
		} else {
			duration = params.duration;
		}
	}
	console.log('duration: ' + duration);
	await timeout(duration);
	
	if (params.functionGraph[functionName] != 'None') {
		const nextFn = getNextFunctions(functionName, params.functionGraph, params.missingFunctionAnomalies);
		await invoke(nextFn, params);
	}
	span.end();
}

module.exports = { main, f };