FROM node:24-alpine

# alpine にはタイムゾーンのデータが入っていないため、TZ=Asia/Tokyo を効かせるために追加する
RUN apk add --no-cache tzdata

WORKDIR /app

# パッケージを先に入れる（package.json が変わらなければ、この層はキャッシュが再利用される）
# package-lock.json* の * は、まだ lock ファイルが無くてもエラーにしないため
COPY package.json package-lock.json* ./
RUN npm install

COPY . .

CMD ["npm", "run", "dev"]
