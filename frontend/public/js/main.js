import { initHealthStatus } from "./health-status.js";

initHealthStatus(document, window.fetch.bind(window));
