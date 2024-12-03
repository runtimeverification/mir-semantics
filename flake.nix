{
  description = "mir-semantics - ";
  inputs = {
    k-framework.url = "github:runtimeverification/k/v7.1.181";
    nixpkgs.follows = "k-framework/nixpkgs";
    flake-utils.follows = "k-framework/flake-utils";
    rv-utils.follows = "k-framework/rv-utils";
    poetry2nix.follows = "k-framework/poetry2nix";
  };
  outputs = { self, nixpkgs, flake-utils, k-framework, ... }@inputs:
    let
      allOverlays = [
        k-framework.overlays.pyk
        (final: prev: let
          poetry2nix =
            inputs.poetry2nix.lib.mkPoetry2Nix { pkgs = prev; };
          in {
          mir-semantics = poetry2nix.mkPoetryApplication {
            python = prev.python310;
            projectDir = ./kmir;
            overrides = poetry2nix.overrides.withDefaults
              (finalPython: prevPython: {
                kframework = prev.pyk-python310;
              });
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
