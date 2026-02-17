// tag.js
// Dummy Express API route for tag analysis

import express from "express";
import multer from "multer";
import * as gpt from "../ai/gpt.js";
import { estimateEmissions } from "../ai/emissions.js";
import fs from "node:fs";
import path from "node:path";

const router = express.Router();
const upload = multer({ dest: "uploads/" });
let tagExtractor = gpt.extractTagFromImage;

export function __setTagExtractorForTest(extractor) {
  tagExtractor = extractor;
}

export function __resetTagExtractorForTest() {
  tagExtractor = gpt.extractTagFromImage;
}

// POST /api/tag - Accepts image upload, returns tag info and CO2 estimate
router.post("/tag", upload.single("image"), async (req, res) => {
  const filePath = req.file?.path;
  if (!filePath) {
    return res.status(400).json({
      error: {
        code: "MISSING_IMAGE",
        message: "An image file is required in field 'image'.",
      },
    });
  }

  try {
    const ext = path.extname(filePath).toLowerCase().replace(".", "");
    const mime =
      ext === "jpg" || ext === "jpeg"
        ? "image/jpeg"
        : ext === "png"
          ? "image/png"
          : "image/jpeg";
    const b64 = fs.readFileSync(filePath, "base64");
    const dataUrl = `data:${mime};base64,${b64}`;

    // Call GPT to extract tag info
    let parsed;
    try {
      parsed = await tagExtractor(dataUrl);
    } catch {
      return res.status(502).json({
        error: {
          code: "UPSTREAM_ERROR",
          message: "Failed to analyze image with AI provider.",
        },
      });
    }
    // Calculate emissions
    const emissions = estimateEmissions(parsed);

    res.json({ parsed, emissions });
  } catch {
    res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Unexpected server error.",
      },
    });
  } finally {
    // Always clean up uploaded file
    if (filePath && fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
  }
});

export default router;
