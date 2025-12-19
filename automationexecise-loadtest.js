import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    // warm up
    { duration: '1m', target: 100 },   // 0 → 100 VUs
    { duration: '2m', target: 100 },   // stay at 100

    // ramp to 1000
    { duration: '3m', target: 500 },   // 100 → 500

    // hold peak load
    { duration: '5m', target: 700 },  // stay at 1000

    // ramp down
    { duration: '2m', target: 0 },     // 1000 → 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests < 2s (more realistic for high load)
    http_req_failed: ['rate<0.05'],   // < 5% errors (more lenient for load testing)
  },
};

const BASE_URL = 'https://automationexercise.com';

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