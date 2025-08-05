# Invensis Recruiters - Deployment Guide

## Prerequisites

Before deploying the application, ensure you have the following installed:

- **Node.js** (v14 or higher)
- **npm** (v6 or higher)
- **MongoDB** (local or cloud instance)
- **Git**

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd invensis-recruiters
   ./setup.sh
   ```

2. **Configure Environment**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit the .env file with your configuration
   nano .env
   ```

3. **Start the Application**
   ```bash
   npm run dev
   ```

4. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
MONGODB_URI=mongodb://localhost:27017/invensis-recruiters

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# Email Configuration (Gmail)
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

# Server Configuration
PORT=5000
```

### Email Setup (Gmail)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. Use the generated password in `EMAIL_PASS`

## MongoDB Setup

### Local MongoDB

1. **Install MongoDB**
   ```bash
   # macOS (using Homebrew)
   brew install mongodb-community
   
   # Ubuntu/Debian
   sudo apt-get install mongodb
   ```

2. **Start MongoDB**
   ```bash
   # macOS
   brew services start mongodb-community
   
   # Ubuntu/Debian
   sudo systemctl start mongodb
   ```

### MongoDB Atlas (Cloud)

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Get your connection string
4. Update `MONGODB_URI` in your `.env` file

## Production Deployment

### Using PM2 (Recommended)

1. **Install PM2**
   ```bash
   npm install -g pm2
   ```

2. **Build the frontend**
   ```bash
   cd client
   npm run build
   cd ..
   ```

3. **Start with PM2**
   ```bash
   pm2 start server/index.js --name "invensis-recruiters"
   pm2 save
   pm2 startup
   ```

### Using Docker

1. **Create Dockerfile**
   ```dockerfile
   FROM node:16-alpine
   
   WORKDIR /app
   
   COPY package*.json ./
   RUN npm install
   
   COPY . .
   RUN cd client && npm install && npm run build
   
   EXPOSE 5000
   
   CMD ["npm", "start"]
   ```

2. **Build and Run**
   ```bash
   docker build -t invensis-recruiters .
   docker run -p 5000:5000 invensis-recruiters
   ```

### Using Heroku

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   ```

2. **Deploy**
   ```bash
   heroku create your-app-name
   heroku config:set MONGODB_URI=your-mongodb-uri
   heroku config:set JWT_SECRET=your-jwt-secret
   heroku config:set EMAIL_USER=your-email
   heroku config:set EMAIL_PASS=your-app-password
   git push heroku main
   ```

## Security Considerations

1. **JWT Secret**: Use a strong, random string for `JWT_SECRET`
2. **MongoDB**: Enable authentication for production databases
3. **Email**: Use environment variables for sensitive credentials
4. **HTTPS**: Use HTTPS in production
5. **File Uploads**: Implement proper file validation and virus scanning
6. **Rate Limiting**: Consider implementing rate limiting for API endpoints

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find process using port 5000
   lsof -i :5000
   # Kill the process
   kill -9 <PID>
   ```

2. **MongoDB connection failed**
   - Check if MongoDB is running
   - Verify connection string in `.env`
   - Check network connectivity

3. **Email not sending**
   - Verify Gmail credentials
   - Check if 2FA is enabled
   - Verify app password is correct

4. **File uploads not working**
   - Check uploads directory permissions
   - Verify file size limits
   - Check file type restrictions

### Logs

- **Backend logs**: Check console output or PM2 logs
- **Frontend logs**: Check browser developer tools
- **MongoDB logs**: Check MongoDB log files

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the application logs
3. Create an issue in the repository
4. Contact the development team

## License

This project is licensed under the MIT License. 