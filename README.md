# 🚀 CodeDeep - Online Judge Platform

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
![Docker](https://img.shields.io/badge/docker-enabled-blue)
![Status](https://img.shields.io/badge/status-active-success)

CodeDeep is a scalable, containerized **online judge platform** developed using Django, Docker, and AWS. It allows users to submit coding solutions which are executed securely in Docker containers and tested against predefined test cases.

---

## ✨ Features

- ✍️ Code submission portal with real-time feedback
- 🧪 Auto-evaluation against input/output test cases
- 📦 Docker-based code execution for safety and isolation
- 🛡 Secure file system and timeout protections
- 🧱 Admin portal for problem management
- 🌐 AWS EC2 deployment ready

---

## ⚙️ Tech Stack

| Layer       | Tech                      |
|-------------|---------------------------|
| Backend     | Python, Django            |
| Execution   | Docker, Shell Scripts     |
| Database    | SQLite3   |
| Frontend    | HTML, CSS (Django Templates) |
| Hosting     | AWS EC2                   |
| VCS & CI    | GitHub, GitHub Actions    |

---

## 📦 Local Setup

```bash
git clone https://github.com/manideep0812/algo_project.git
cd algo_project
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
