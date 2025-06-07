FROM node:18

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# No build step here! Just run dev server
EXPOSE 3000
CMD ["npm", "start"]
