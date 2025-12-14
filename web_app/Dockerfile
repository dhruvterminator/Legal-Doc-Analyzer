# # Specify the base image
# FROM node:16-alpine


# # Set the working directory
# WORKDIR /app

# # Copy the package.json and package-lock.json files
# COPY package*.json ./

# # Install dependencies
# RUN npm install

# # Copy the source code
# COPY . .

# # Build the Next.js app
# RUN npm run build

# # Set the command to start the Next.js app
# CMD ["npm", "run","dev"]
FROM node:16


WORKDIR /app

# Copy package files first (important for caching)
COPY package*.json ./

# Install dependencies (THIS WAS MISSING)
RUN npm install

# Copy rest of the app
COPY . .

# Expose Next.js port
EXPOSE 3000

# Start Next.js
CMD ["npm", "run", "dev"]

