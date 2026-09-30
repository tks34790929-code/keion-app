FROM node:24-alpine

WORKDIR /app

# パッケージを先に入れる（package.json が変わらなければ、この層はキャッシュが再利用される）
# package-lock.json* の * は、まだ lock ファイルが無くてもエラーにしないため
COPY package.json package-lock.json* ./
RUN npm install

COPY . .

CMD ["npm", "run", "dev"]
