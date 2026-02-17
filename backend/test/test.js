// test.js
// Test script to POST an image to the /api/tag endpoint

import fs from "node:fs";
import path from "node:path";
import axios from "axios";
import FormData from "form-data";

// ES module workaround for __dirname
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function runTest() {
  const imagePath = path.join(__dirname, "test_image.jpg");
  const form = new FormData();
  form.append("image", fs.createReadStream(imagePath));

  try {
    const response = await axios.post("http://localhost:3001/api/tag", form, {
      headers: form.getHeaders(),
    });
    console.log("Response:", response.data);
  } catch (err) {
    console.error("Error:", err.response?.data || err.message);
  }
}

runTest();
