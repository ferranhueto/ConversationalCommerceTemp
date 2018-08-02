# Use an official node runtime as a parent image
FROM node:8

# Set the working directory to /websocket_server
WORKDIR /websocket_server
# Copy the current directory contents into the container at /websocket_server
ADD ./websocket_server /websocket_server
# Copy the contents at /Node directory contents into the container at /Node
ADD ./Node /websocket_server/Node

## NOTE : git-lfs stuff is done before image is built

# Install dependencies
RUN npm install

# Expose port 8000
EXPOSE 8000

# Run ws.js when the container launches
CMD ["node", "ws.js"]
