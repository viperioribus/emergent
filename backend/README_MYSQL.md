# Beach Informs Backend - MySQL Version

## Overview
This backend is designed to work with your existing MySQL database with the `usuarios` table schema.

## Database Schema

### Existing Table (usuarios)
```sql
CREATE TABLE `usuarios` (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `login` varchar(50) COLLATE latin1_spanish_ci NOT NULL,
  `password` varchar(50) COLLATE latin1_spanish_ci NOT NULL,
  `nombre` varchar(20) COLLATE latin1_spanish_ci NOT NULL,
  `apellido1` varchar(20) COLLATE latin1_spanish_ci NOT NULL,
  `apellido2` varchar(20) COLLATE latin1_spanish_ci NOT NULL,
  `email` varchar(50) COLLATE latin1_spanish_ci NOT NULL,
  `language` varchar(30) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `isAdmin` int(1) UNSIGNED NOT NULL DEFAULT '0',
  `foto` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `idperfil` int(11) UNSIGNED NOT NULL,
  `idmunicipio` int(11) UNSIGNED NOT NULL,
  `aplicacion` varchar(15) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
```

### New Tables (Auto-created on startup)

**beaches**
```sql
CREATE TABLE beaches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**beach_posts**
```sql
CREATE TABLE beach_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    beach_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_beach_id (beach_id),
    FOREIGN KEY (beach_id) REFERENCES beaches(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**inform2_submissions**
```sql
CREATE TABLE inform2_submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    beach_name VARCHAR(200) NOT NULL,
    hour INT NOT NULL,
    minute INT NOT NULL,
    person_name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    incidences TEXT NOT NULL,  -- JSON array of selected incidences
    observations TEXT,
    username VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_date (date),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**inform4_submissions**
```sql
CREATE TABLE inform4_submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    beach_name VARCHAR(200) NOT NULL,
    hour INT NOT NULL,
    minute INT NOT NULL,
    wind_speed DECIMAL(5,2) NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    wave_height DECIMAL(5,2) NOT NULL,
    username VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_date (date),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Configuration

### Environment Variables (.env)
```bash
# MySQL Connection
MYSQL_HOST="your_mysql_host"
MYSQL_PORT="3306"
MYSQL_USER="your_mysql_user"
MYSQL_PASSWORD="your_mysql_password"
MYSQL_DB="your_database_name"

# JWT Configuration
JWT_SECRET_KEY="change-this-to-a-secure-random-string"
```

## API Endpoints

### Authentication
- **POST** `/api/auth/login`
  - Body: `{"login": "username", "password": "password"}`
  - Returns: `{"access_token": "jwt_token", "token_type": "bearer"}`
  - Uses existing `usuarios` table with `login` and `password` fields

### Beaches (Requires Authentication)
- **GET** `/api/beaches`
  - Headers: `Authorization: Bearer {token}`
  - Returns: List of beaches with id and name

- **GET** `/api/beach-posts/{beach_id}`
  - Headers: `Authorization: Bearer {token}`
  - Returns: List of beach posts for the specified beach

### Informs (Requires Authentication)
- **POST** `/api/inform2`
  - Headers: `Authorization: Bearer {token}`
  - Body:
    ```json
    {
      "date": "2024-12-24",
      "beach_name": "Santa Monica Beach - Post A",
      "hour": 14,
      "minute": 30,
      "person_name": "John Doe",
      "age": 35,
      "postal_code": "90401",
      "incidences": ["wound cuts, grazes", "sting"],
      "observations": "Minor incident"
    }
    ```

- **POST** `/api/inform4`
  - Headers: `Authorization: Bearer {token}`
  - Body:
    ```json
    {
      "date": "2024-12-24",
      "beach_name": "Venice Beach - Post B",
      "hour": 15,
      "minute": 0,
      "wind_speed": 12.5,
      "temperature": 22.3,
      "wave_height": 1.8
    }
    ```

## Deployment on CentOS with PHP Server

### Option 1: Python FastAPI (Recommended)
1. Install Python 3.11+ on your CentOS server
2. Install dependencies: `pip install -r requirements.txt`
3. Configure .env with your MySQL credentials
4. Run with: `uvicorn server:app --host 0.0.0.0 --port 8001`
5. Set up systemd service for auto-start
6. Use nginx as reverse proxy to route `/api/*` to the Python backend

### Option 2: PHP Backend (Alternative)
If you prefer PHP, I can create a PHP version that provides the same API endpoints using your existing PHP server infrastructure.

## Security Notes
1. The backend supports both bcrypt hashed passwords (for new users) and plain text passwords (for compatibility with existing users)
2. JWT tokens expire after 24 hours
3. All authenticated endpoints require a valid Bearer token
4. Update JWT_SECRET_KEY in production to a secure random string

## Sample Data
On first startup, the backend automatically creates:
- 3 sample beaches: Santa Monica Beach, Venice Beach, Malibu Beach
- 3 beach posts for each beach: Post A, Post B, Post C

## Testing
```bash
# Login
curl -X POST http://your-server:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login": "your_username", "password": "your_password"}'

# Get beaches (replace TOKEN with actual token)
curl -X GET http://your-server:8001/api/beaches \
  -H "Authorization: Bearer TOKEN"
```

## Requirements
- Python 3.11+
- MySQL 5.7+ or MariaDB 10.3+
- Required Python packages listed in requirements.txt
