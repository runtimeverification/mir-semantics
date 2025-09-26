{
  description = "kmir - ";
  inputs = {
    rv-nix-tools.follows = "k-framework/rv-nix-tools";
    nixpkgs.follows = "rv-nix-tools/nixpkgs";

    flake-utils.url = "github:numtide/flake-utils";

    stable-mir-json-flake.url = "github:runtimeverification/stable-mir-json/8dcacda4d94f10ea102884887e56da335e4d161c";
    stable-mir-json-flake = {
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };

    k-framework.url = "github:runtimeverification/k/v7.1.286";
    k-framework = {
      inputs.flake-utils.follows = "flake-utils";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix.url = "github:pyproject-nix/uv2nix/680e2f8e637bc79b84268949d2f2b2f5e5f1d81c";
    # stale nixpkgs is missing the alias `lib.match` -> `builtins.match`
    # therefore point uv2nix to a patched nixpkgs, which introduces this alias
    # this is a temporary solution until nixpkgs us up-to-date again
    uv2nix.inputs.nixpkgs.url = "github:runtimeverification/nixpkgs/libmatch";
    # inputs.nixpkgs.follows = "nixpkgs";
    pyproject-build-systems.url = "github:pyproject-nix/build-system-pkgs/7dba6dbc73120e15b558754c26024f6c93015dd7";
    pyproject-build-systems = {
      inputs.nixpkgs.follows = "uv2nix/nixpkgs";
      inputs.uv2nix.follows = "uv2nix";
      inputs.pyproject-nix.follows = "uv2nix/pyproject-nix";
    };
    pyproject-nix.follows = "uv2nix/pyproject-nix";
  };
  outputs = {
    self,
    nixpkgs,
    rv-nix-tools,
    flake-utils,
    stable-mir-json-flake,
    k-framework,
    pyproject-nix,
    pyproject-build-systems,
    uv2nix
  }:
  let
    pythonVer = "310";
  in flake-utils.lib.eachDefaultSystem (system:
    let
      uvOverlay = final: prev: {
        uv = uv2nix.packages.${final.system}.uv-bin;
      };
      # create custom overlay for k, because the overlay in k-framework currently also includes a lot of other stuff instead of only k
      kOverlay = final: prev: {
        k = k-framework.packages.${final.system}.k;
      };
      stable-mir-json-overlay = final: prev: {
        stable-mir-json = stable-mir-json-flake.packages.${final.system}.stable-mir-json;
      };
      kmir-overlay = final: prev:
      let
        kmir-pyk = final.callPackage ./nix/kmir-pyk {
          inherit pyproject-nix pyproject-build-systems uv2nix;
          python = final."python${pythonVer}";
        };
        kmir = final.callPackage ./nix/kmir {
          inherit kmir-pyk;
          rev = self.rev or null;
        };
      in {
        inherit kmir-pyk kmir;
      };
      pkgs = import nixpkgs {
        inherit system;
        overlays = [
          uvOverlay
          kOverlay
          stable-mir-json-overlay
          kmir-overlay
        ];
      };
      python = pkgs."python${pythonVer}";
    in {
      devShells.default =
      let
        stable-mir-json-shell = stable-mir-json-flake.devShells.${system}.default;
      in pkgs.mkShell {
        name = "uv and rust develop shell";
        # we use the stable-mir-json nix develop shell as a basis
        # because the mir-semantics Makefile builds stable-mir-json in a submodule directory
        buildInputs = (stable-mir-json-shell.buildInputs or []) ++ [
          python
          pkgs.uv
        ];
        env = (stable-mir-json-shell.env or { }) // {
          # prevent uv from managing Python downloads and force use of specific 
          UV_PYTHON_DOWNLOADS = "never";
          UV_PYTHON = python.interpreter;
        };
        shellHook = (stable-mir-json-shell.shellHook or "") + ''
          unset PYTHONPATH
        '';
      };
      packages = rec {
        inherit (pkgs) kmir-pyk kmir;
        default = kmir;
      };
    }) // {
      overlays.default = final: prev: {
        inherit (self.packages.${final.system}) kmir;
      };
    };
}
