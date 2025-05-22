const express = require("express");
const routes = require("./api/routes");
const morgan = require("morgan");

const app = express();
app.use(express.json());
app.use(morgan("dev"));
app.use("/", routes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Contracts server running on port ${PORT}`);
});
