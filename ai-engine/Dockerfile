# Multi-stage build para otimizar o tamanho da imagem
FROM rust:1.75-alpine AS builder

# Instalar dependências do sistema
RUN apk add --no-cache musl-dev pkgconfig openssl-dev

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de configuração
COPY Cargo.toml Cargo.lock ./

# Criar estrutura de diretórios
RUN mkdir src && echo "fn main() {}" > src/main.rs

# Build de dependências (cache layer)
RUN cargo build --release

# Remover código dummy
RUN rm -rf src

# Copiar código fonte
COPY src/ ./src/

# Build da aplicação
RUN cargo build --release

# Estágio de produção
FROM alpine:latest

# Instalar dependências de runtime
RUN apk add --no-cache ca-certificates

# Criar usuário não-root
RUN addgroup -g 1001 -S rust
RUN adduser -S rust -u 1001

# Definir diretório de trabalho
WORKDIR /app

# Copiar binário da aplicação
COPY --from=builder /app/target/release/smart-city-ai ./smart-city-ai

# Alterar propriedade dos arquivos
RUN chown -R rust:rust /app
USER rust

# Expor porta
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8081/health || exit 1

# Comando para iniciar a aplicação
CMD ["./smart-city-ai"]
