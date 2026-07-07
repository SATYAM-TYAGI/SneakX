FROM node:18-alpine

WORKDIR /app

# Copy package descriptors and install dependencies
COPY package*.json ./
RUN npm install

# Copy application files
COPY . .

# Expose Vite development port
EXPOSE 3000

# Start Vite server
CMD ["npm", "run", "dev"]
