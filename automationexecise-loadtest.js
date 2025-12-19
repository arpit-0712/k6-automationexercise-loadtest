import http from 'k6/http';
import { check, sleep } from 'k6';

// Get max users from environment variable, default to 500
const MAX_USERS = __ENV.MAX_USERS ? parseInt(__ENV.MAX_USERS) : 500;

// Calculate stage targets based on max users
const WARMUP_TARGET = Math.min(100, Math.floor(MAX_USERS * 0.2)); // 20% or max 100
const RAMP_TARGET = Math.floor(MAX_USERS * 0.5); // 50% of max
const PEAK_TARGET = MAX_USERS; // 100% of max

export const options = {
  stages: [
    // warm up
    { duration: '1m', target: WARMUP_TARGET },   // 0 → warmup VUs
    { duration: '2m', target: WARMUP_TARGET },   // stay at warmup

    // ramp to peak
    { duration: '3m', target: RAMP_TARGET },   // warmup → ramp

    // hold peak load
    { duration: '5m', target: PEAK_TARGET },  // stay at peak

    // ramp down
    { duration: '2m', target: 0 },     // peak → 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests < 2s (more realistic for high load)
    http_req_failed: ['rate<0.05'],   // < 5% errors (more lenient for load testing)
  },
};

const BASE_URL = 'https://demoqa.com/';

export default function () {
  // Home page
  const homeRes = http.get(`${BASE_URL}/`);
  check(homeRes, {
    'home status is 200': (r) => r.status === 200,
  });

  // Products page
  const productsRes = http.get(`${BASE_URL}/products`);
  check(productsRes, {
    'products status is 200': (r) => r.status === 200,
  });

  // Simulated user think-time between actions
  sleep(1);
}