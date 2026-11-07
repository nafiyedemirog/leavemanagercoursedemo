import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { JSDOM } from "jsdom";

import { MESSAGES, initHealthStatus } from "../public/js/health-status.js";

const INDEX_HTML = readFileSync(new URL("../public/index.html", import.meta.url), "utf8");

// The real page, without running its scripts: the test drives the module directly.
function loadPage() {
  return new JSDOM(INDEX_HTML).window.document;
}

function statusText(doc) {
  return doc.getElementById("health-status").textContent;
}

function jsonResponse(ok, body) {
  return { ok, status: ok ? 200 : 500, json: async () => body };
}

test("test_shows_checking_text_while_request_pending", async () => {
  const doc = loadPage();
  assert.equal(statusText(doc), MESSAGES.checking, "initial page text");

  initHealthStatus(doc, () => new Promise(() => {})); // never settles
  await Promise.resolve();

  assert.equal(statusText(doc), "Sistem durumu kontrol ediliyor…");
  const region = doc.getElementById("health-status");
  assert.equal(region.getAttribute("aria-live"), "polite");
});

test("test_shows_running_text_on_success", async () => {
  const doc = loadPage();
  const calls = [];
  const fetchFn = async (url) => {
    calls.push(url);
    return jsonResponse(true, { status: "ok" });
  };

  const state = await initHealthStatus(doc, fetchFn);

  assert.equal(state, "running");
  assert.equal(statusText(doc), "Sistem çalışıyor");
  assert.deepEqual(calls, ["/api/health"]);
});

test("test_shows_error_text_on_network_failure", async () => {
  const doc = loadPage();
  const fetchFn = async () => {
    throw new TypeError("Failed to fetch");
  };

  const state = await initHealthStatus(doc, fetchFn);

  assert.equal(state, "error");
  assert.equal(statusText(doc), "Sistem şu anda yanıt vermiyor. Lütfen daha sonra tekrar deneyin.");
});

test("test_shows_error_text_on_error_response_without_html", async () => {
  const doc = loadPage();
  const hostile = '<img src="x" onerror="alert(1)">';
  const fetchFn = async () =>
    jsonResponse(false, { type: "internal-error", status: 500, detail: hostile });

  const state = await initHealthStatus(doc, fetchFn);

  assert.equal(state, "error");
  assert.equal(statusText(doc), MESSAGES.error);
  assert.equal(doc.querySelector("img"), null, "no element created from server content");
  assert.equal(doc.getElementById("health-status").children.length, 0);
});
