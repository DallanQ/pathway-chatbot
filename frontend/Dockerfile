FROM node:20-alpine as build

WORKDIR /app
ARG NEXT_PUBLIC_CHAT_API
ARG NEXT_PUBLIC_CHAT_API

# Install dependencies
COPY package.json package-lock.* ./
RUN npm install

# Build the application
COPY . .
RUN npm run build

# setting them to ENV if needed in the build
ENV NEXT_PUBLIC_CHAT_API=$NEXT_PUBLIC_CHAT_API

# ====================================
FROM build as release

CMD ["npx", "-y", "serve@latest", "out"]