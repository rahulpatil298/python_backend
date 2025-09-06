SafeAI: Your AI-Powered Companion for Safe Adventures
SafeAI is a mobile application designed to enhance personal safety and provide powerful, AI-assisted navigation for your outdoor activities. Whether you're a lone traveler, an adventure enthusiast, or a corporate professional on the move, SafeAI is your one-stop solution for a secure and connected experience.

Live Link: https://safeai.onrender.com

✨ Features
Emergency SOS: In an emergency, simply saying "Help" or tapping the emergency button instantly alerts your loved ones and dispatches emergency services with your live location.

Intelligent Route Planning: Plan your cycling, running, or walking routes. The AI assistant helps you find interesting locations and nearby events, like marathons or trail runs, to make your adventures more engaging.

Corporate Workforce Management: SafeAI offers a robust corporate solution to monitor employee locations, attendance, and tasks. Features include:

Geofencing: Create and manage geofenced zones to track workforce activity, ensuring employees are on-site for their assigned hours.

Real-time Monitoring: View live status (online, on-field, offline), last arrival times, and assigned tasks for all employees.

AI-Powered Assistance: A conversational AI assistant is integrated into the app to help with route planning and other queries, providing personalized recommendations and information.

Authentication: The app supports multiple authentication types, including quick login for general users and dedicated logins for corporate and employee accounts.

⚙️ Technology Stack
This project is a full-stack application leveraging modern, scalable technologies.

Frontend:

Flutter: The mobile application is built with Flutter, enabling a single codebase for both iOS and Android.

React: A web-based frontend is also developed with React to provide a dashboard for corporate features.

Backend:

Node.js: The backend server is built with Node.js for high performance and scalability.

AI Model: The AI assistant uses an LLM (Large Language Model) to provide intelligent and context-aware responses, likely utilizing a RAG (Retrieval-Augmented Generation) architecture to access relevant, up-to-date information.

Database:

MongoDB: Stores user data, geofencing configurations, and other application-specific information.

Mapping & Location Services:

MapmyIndia: Powers the mapping, geofencing, and navigation features.

Deployment:

Render: The backend is deployed on Render, a cloud platform for running web services and APIs.

📂 Project Structure
client/: The source code for the Flutter mobile application.

server/: The backend server code, built with Node.js and the AI integration logic.

shared/: Shared components, types, and utilities used by both the client and server.

.env.example: A template for environment variables required to run the project.

🤝 Contribution
We welcome contributions! If you have suggestions for new features, bug fixes, or improvements, feel free to open an issue or submit a pull request.
