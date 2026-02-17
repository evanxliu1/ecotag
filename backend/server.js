// server.js
// Express app entry point

import express from "express";
import tagRouter from "./api/tag.js";

const app = express();
app.use(express.json());
app.use("/api", tagRouter);

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
