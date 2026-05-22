const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();
const PORT = Number(process.env.PORT || 8080);
const API_BASE_URL = process.env.API_BASE_URL || '/api';
const API_UPSTREAM = process.env.API_UPSTREAM || 'http://api:3000';

// Servir archivos estáticos desde la carpeta 'public'
app.use(express.static(path.join(__dirname, 'public')));

app.use(
    API_BASE_URL,
    createProxyMiddleware({
        target: API_UPSTREAM,
        changeOrigin: true
    })
);

app.get('/config.js', (req, res) => {
    res.type('application/javascript');
    res.send(`window.APP_CONFIG = { API_BASE_URL: '${API_BASE_URL}' };`);
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Frontend Node.js corriendo en http://localhost:${PORT}`);
});