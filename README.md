# 🎨 Pixero

**Pixero** is a platform that connects photographers and video editors with clients looking for creative services.

## ✨ Features

- **Creator Registration** — Photographers and editors can register with their profiles, services, and portfolio
- **Browse Creators** — Clients can browse photographers and editors by location
- **Portfolio View** — Detailed portfolio pages for each creator
- **Creator Login** — Search and manage creator profiles via email
- **Reviews** — Clients can submit and view reviews
- **Contact Us** — Get in touch with the Pixero team

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Database**: MySQL
- **Deployment**: Render

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- MySQL Server

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/prathamchandak25-oss/pixero.git
   cd pixero
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the MySQL database:
   ```bash
   mysql -u root -p < databasse.sql
   mysql -u root -p < review.sql
   ```

4. Create a `.env` file with your database credentials:
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   ```

5. Run the application:
   ```bash
   python backened.py
   ```

6. Open `http://localhost:5000` in your browser.

## 👥 Team

- Pratham Chandak
- Prathamesh
- Vedant

## 📄 License

This project is part of a Semester 4 academic project.
