require('dotenv').config();
const express = require('express');
const { Pool } = require('pg');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(express.json());
app.use(cors());

// FIX: Go UP one level from /api to find the /public folder
app.use(express.static(path.join(__dirname, '../public')));

// DATABASE CONNECTION - Wrapped in try/catch to prevent total server crash
let pool;
try {
    pool = new Pool({ 
        connectionString: process.env.DATABASE_URL,
        ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false 
    });
    console.log("✅ DB Pool Initialized");
} catch (err) {
    console.error("❌ DB Connection Error:", err);
}

const JWT_SECRET = process.env.JWT_SECRET || 'fallback_secret_for_dev';

// HEALTH CHECK: Visit your-url.vercel.app/health
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        message: 'Server is running!',
        db_configured: !!process.env.DATABASE_URL 
    });
});

async function initDb() {
    if (!pool) return;
    try {
        await pool.query(`
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS identities (
                id SERIAL PRIMARY KEY,
                group_id TEXT NOT NULL,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                base_email TEXT,
                username TEXT,
                email TEXT,
                active BOOLEAN DEFAULT false,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        `);
        console.log("✅ Database Schema Ready");
    } catch (err) {
        console.error("❌ DB Init Error:", err);
    }
}
initDb();

const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    if (!token) return res.status(401).json({ error: "Authentication required" });

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.status(403).json({ error: "Invalid or expired token" });
        req.user = user;
        next();
    });
};

app.post('/api/signup', async (req, res) => {
    if (!pool) return res.status(500).json({ error: "Database not connected" });
    const { email, password } = req.body;
    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        await pool.query('INSERT INTO users (email, password) VALUES ($1, $2)', [email, hashedPassword]);
        res.json({ success: true });
    } catch (e) {
        res.status(400).json({ error: "Email already registered" });
    }
});

app.post('/api/login', async (req, res) => {
    if (!pool) return res.status(500).json({ error: "Database not connected" });
    const { email, password } = req.body;
    try {
        const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
        const user = result.rows[0];
        if (user && await bcrypt.compare(password, user.password)) {
            const token = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET, { expiresIn: '7d' });
            res.json({ token, email: user.email });
        } else {
            res.status(401).json({ error: "Invalid credentials" });
        }
    } catch (e) {
        res.status(500).json({ error: "Server error" });
    }
});

app.get('/api/identities', authenticateToken, async (req, res) => {
    if (!pool) return res.status(500).json({ error: "Database not connected" });
    try {
        const result = await pool.query('SELECT * FROM identities WHERE user_id = $1 ORDER BY created DESC', [req.user.id]);
        res.json(result.rows);
    } catch (e) {
        res.status(500).json({ error: "Fetch failed" });
    }
});

app.post('/api/identities', authenticateToken, async (req, res) => {
    if (!pool) return res.status(500).json({ error: "Database not connected" });
    const { groupId, baseEmail, identities } = req.body;
    try {
        for (const iden of identities) {
            await pool.query(
                'INSERT INTO identities (group_id, user_id, base_email, username, email, active) VALUES ($1, $2, $3, $4, $5, $6)',
                [groupId, req.user.id, baseEmail, iden.username, iden.email, iden.active]
            );
        }
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ error: "Failed to save identities" });
    }
});

app.patch('/api/identities/:id', authenticateToken, async (req, res) => {
    if (!pool) return res.status(500).json({ error: "Database not connected" });
    const { active, username } = req.body;
    try {
        await pool.query(
            'UPDATE identities SET active = COALESCE($1, active), username = COALESCE($2, username) WHERE id = $3 AND user_id = $4',
            [active, username, req.params.id, req.user.id]
        );
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ error: "Update failed" });
    }
});

app.delete('/api/identities/group/:groupId', authenticateToken, async (req, res) => {
    if (!pool) return res.status(500).json({ error: "Database not connected" });
    try {
        await pool.query('DELETE FROM identities WHERE group_id = $1 AND user_id = $2', [req.params.groupId, req.user.id]);
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ error: "Delete failed" });
    }
});

// FIX: Go UP one level from /api to find the /public/index.html
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../public', 'index.html'));
});

if (process.env.NODE_ENV !== 'production') {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`🚀 Local: http://localhost:${PORT}`);
    });
}

module.exports = app;
