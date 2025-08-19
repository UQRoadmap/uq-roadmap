# Chef
FROM clux/muslrust:1.90.0-nightly AS chef
USER root
RUN cargo install cargo-chef
WORKDIR /app

# Caching stuff for chef
FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json --bin backend2

# Build the app
FROM chef AS builder 
COPY --from=planner /app/recipe.json recipe.json
RUN cargo chef cook --release --target x86_64-unknown-linux-musl --recipe-path recipe.json --bin backend2
COPY . .
ENV SQLX_OFFLINE=true
RUN cargo build --release --target x86_64-unknown-linux-musl --bin backend2

# Container:
FROM alpine AS runtime
RUN apk add --no-cache openssh-keygen openssl su-exec wget ca-certificates nss-tools
RUN addgroup -S user && adduser -S user -G user
WORKDIR /app
COPY --from=builder /app/target/x86_64-unknown-linux-musl/release/backend2 /usr/local/bin/
ENTRYPOINT ["/usr/local/bin/backend2"]
