const { app, BrowserWindow } = require("electron");

const FRONTEND_URL = process.env.ZERENTHIS_FRONTEND_URL || "http://localhost:5173";
const APP_TITLE = "Zerenthis Founder";

function createWindow() {
  const win = new BrowserWindow({
    width: 1440,
    height: 920,
    minWidth: 1100,
    minHeight: 700,
    title: APP_TITLE,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.loadURL(FRONTEND_URL);
}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
