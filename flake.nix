{
  description = "kmir - ";
  inputs = {
    rv-nix-tools.url = "github:runtimeverification/rv-nix-tools/854d4f05ea78547d46e807b414faad64cea10ae4";
    nixpkgs.follows = "rv-nix-tools/nixpkgs";

    flake-utils.url = "github:numtide/flake-utils";

    stable-mir-json-flake.url = "github:runtimeverification/stable-mir-json/b54152a3099c4756c31fea1a126c20167ae42798";
    stable-mir-json-flake = {
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };

    k-framework.url = "github:runtimeverification/k/v7.1.289";
    k-framework = {
      inputs.flake-utils.follows = "flake-utils";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix.url = "github:pyproject-nix/uv2nix/64298e806f4a5f63a51c625edc100348138491aa";
    # uv2nix requires a newer version of nixpkgs
    # therefore, we pin uv2nix specifically to a newer version of nixpkgs
    # until we replaced our stale version of nixpkgs with an upstream one as well
    # but also uv2nix requires us to call it with `callPackage`, so we add stuff
    # from the newer nixpkgs to our stale nixpkgs via an overlay
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";
    uv2nix.inputs.nixpkgs.follows = "nixpkgs-unstable";
    # uv2nix.inputs.nixpkgs.follows = "nixpkgs";
    pyproject-build-systems.url = "github:pyproject-nix/build-system-pkgs/7dba6dbc73120e15b558754c26024f6c93015dd7";
    pyproject-build-systems = {
      inputs.nixpkgs.follows = "uv2nix/nixpkgs";
      inputs.uv2nix.follows = "uv2nix";
      inputs.pyproject-nix.follows = "uv2nix/pyproject-nix";
    };
    pyproject-nix.follows = "uv2nix/pyproject-nix";
  };
  outputs =
    {
      self,
      nixpkgs,
      rv-nix-tools,
      flake-utils,
      stable-mir-json-flake,
      k-framework,
      pyproject-nix,
      pyproject-build-systems,
      uv2nix,
      nixpkgs-unstable,
    }:
    let
      pythonVer = "310";
    in
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs-unstable = import nixpkgs-unstable { inherit system; };
        # for uv2nix, remove this once we updated to a newer version of nixpkgs
        staleNixpkgsOverlay = final: prev: { inherit (pkgs-unstable) replaceVars; };
        uvOverlay = final: prev: { uv = uv2nix.packages.${final.system}.uv-bin; };
        # create custom overlay for k, because the overlay in k-framework currently also includes a lot of other stuff instead of only k
        kOverlay = final: prev: { k = k-framework.packages.${final.system}.k; };
        stable-mir-json-overlay =
          final: prev:
          let
            stable-mir-json-packages = stable-mir-json-flake.packages.${final.system};
          in
          {
            inherit (stable-mir-json-packages) stable-mir-json;
            stable-mir-json-rust = stable-mir-json-packages.rustToolchain;
          };
        kmir-overlay =
          final: prev:
          let
            rev = self.rev or null;
            kmir-pyk = final.callPackage ./nix/kmir-pyk {
              inherit pyproject-nix pyproject-build-systems uv2nix;
              python = final."python${pythonVer}";
            };
            kmir = final.callPackage ./nix/kmir { inherit kmir-pyk rev; };
            kmir-package-test = final.callPackage ./nix/test/package.nix { inherit rev; };
          in
          {
            inherit kmir-pyk kmir kmir-package-test;
          };
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            staleNixpkgsOverlay
            uvOverlay
            kOverlay
            stable-mir-json-overlay
            kmir-overlay
          ];
        };
        python = pkgs."python${pythonVer}";
      in
      {
        devShells.default =
          let
            stable-mir-json-shell = stable-mir-json-flake.devShells.${system}.default;
          in
          pkgs.mkShell {
            name = "uv and rust develop shell";
            # we use the stable-mir-json nix develop shell as a basis
            # because the mir-semantics Makefile builds stable-mir-json in a submodule directory
            buildInputs = (stable-mir-json-shell.buildInputs or [ ]);
            packages = (stable-mir-json-shell.packages or [ ]) ++ [
              python
              pkgs.uv
            ];
            env = (stable-mir-json-shell.env or { }) // {
              # prevent uv from managing Python downloads and force use of specific 
              UV_PYTHON_DOWNLOADS = "never";
              UV_PYTHON = python.interpreter;
            };
            shellHook =
              (stable-mir-json-shell.shellHook or "")
              + ''
                unset PYTHONPATH
              '';
          };

        packages = rec {
          inherit (pkgs) kmir-pyk kmir;
          default = kmir;
        };

        checks = {
          inherit (pkgs) kmir-package-test;
        };

        # note: this package will be renamed to `nixfmt` in probably 25.11
        #       and already was renamed in unstable
        formatter = pkgs.nixfmt-rfc-style;
      }
    )
    // {
      overlays.default = final: prev: { inherit (self.packages.${final.system}) kmir; };
    };
}
