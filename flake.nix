{
  description = " A flake for KMIR Semantics";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/f971f35f7d79c53a83c7b10de953f1db032cba0e"; # Same as KEVM and KAVM
    k-framework.url = "github:runtimeverification/k/v6.0.44";
    # k-framework.inputs.nixpkgs.follows = "nixpkgs";
    flake-utils.follows = "k-framework/flake-utils";
    rv-utils.url = "github:runtimeverification/rv-nix-tools";
    poetry2nix.url = "github:nix-community/poetry2nix/master";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
  };
  outputs = { self, k-framework, nixpkgs, flake-utils, poetry2nix, rv-utils }:
    let
      allOverlays = [
        poetry2nix.overlay
        (final: prev: {
          kmir-pyk = prev.poetry2nix.mkPoetryApplication {
            python = final.python310;
            projectDir = ./kmir;
            overrides = prev.poetry2nix.overrides.withDefaults (finalPython: prevPython: {
              pyk = prevPython.pyk.overridePythonAttrs (old: {
                groups = [];
                # We remove `dev` from `checkGroups`, so that poetry2nix does not try to resolve dev dependencies.
                checkGroups = [];
                propagatedBuildInputs = (old.propagatedBuildInputs or [ ]) ++ [ finalPython.poetry ];
              });
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
          inherit (pkgs) kmir-pyk;
          default = kmir-pyk;
      #  = pkgs..pyk;
        };
      }) // {
        overlays.default = nixpkgs.lib.composeManyExtensions allOverlays;
      };
}
