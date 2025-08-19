{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    rust-overlay.url = "github:oxalica/rust-overlay";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      rust-overlay,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        overlays = [ (import rust-overlay) ];
        pkgs = import nixpkgs {
          inherit system overlays;
        };
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            openssl
            pkg-config
            glib
            cargo-watch
            rustfmt
            (rust-bin.selectLatestNightlyWith (
              toolchain:
              toolchain.default.override {
                extensions = [
                  "rust-src"
                  "rustc-codegen-cranelift-preview"
                  "rust-analyzer"
                  "clippy"
                ];
              }
            ))
          ];

          RUST_SRC_PATH = "${pkgs.rust.packages.stable.rustPlatform.rustLibSrc}";
        };
      }
    );
}
