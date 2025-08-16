export const BACKEND_BASE_URL = process.env.BACKEND_URL;

if (!BACKEND_BASE_URL) {
  throw new Error("BACKEND_URL environment variable is not defined");
}