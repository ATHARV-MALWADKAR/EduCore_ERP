# Dockerfile for Reflex Frontend
FROM node:18-alpine as base

WORKDIR /app

# Install python (needed for some Reflex dependencies)
RUN apk add --no-cache python3 py3-pip

# Copy package files
COPY rxconfig.py .

# Install Reflex globally
RUN pip install --no-cache-dir reflex==0.3.2

# Copy frontend code
COPY college_erp ./college_erp

# Build the frontend
RUN reflex export --no-zip

EXPOSE 3000 3001

CMD ["reflex", "run"]
