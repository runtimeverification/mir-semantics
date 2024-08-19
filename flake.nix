{
  description = "mir-semantics - ";
  inputs = {
    k-framework.url = "github:runtimeverification/k/v7.1.112";
    nixpkgs.follows = "k-framework/nixpkgs";
    flake-utils.follows = "k-framework/flake-utils";
    rv-utils.follows = "k-framework/rv-utils";
    pyk.url = "github:runtimeverification/k/v7.1.112?dir=pyk";
    nixpkgs-pyk.follows = "pyk/nixpkgs";
    poetry2nix.follows = "pyk/poetry2nix";
  };
  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    let
      allOverlays = [
        poetry2nix.overlay
        (final: prev: {
          mir-semantics = prev.poetry2nix.mkPoetryApplication {
            python = prev.python310;
            projectDir = ./.;
            groups = [];
            # We remove `dev` from `checkGroups`, so that poetry2nix does not try to resolve dev dependencies.
            checkGroups = [];
           };
        })
      ];
    in flake-utils.lib.eachSystem [
      "x86_64-linux"
      "x86_64-darwin"
      "aarch64-linux"
      "aarch64-darwin"
    ] (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = allOverlays;
        };
      in {
        packages = rec {
          inherit (pkgs) mir-semantics;
          default = mir-semantics;
        };
      }) // {
        overlay = nixpkgs.lib.composeManyExtensions allOverlays;
      };
}
