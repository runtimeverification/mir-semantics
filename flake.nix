{
  description = " A flake for KMIR Semantics";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/"; # Same as KEVM and KAVM
    k-framework.url = "github:runtimeverification/k/v6.0.44";
    # k-framework.inputs.nixpkgs.follows = "nixpkgs";
    flake-utils.follows = "k-framework/flake-utils";
    rv-utils.url = "github:runtimeverification/rv-nix-tools";
    poetry2nix.url = "github:nix-community/poetry2nix/master";
    pyk.url = "github:runtimeverification/pyk/v0.1.401";
    pyk.inputs.flake-utils.follows = "k-framework/flake-utils";
    pyk.inputs.nixpkgs.follows = "k-framework/nixpkgs";
  };
  outputs = { self, k-framework, nixpkgs, flake-utils, poetry2nix, rv-utils, pyk }:
    let
      allOverlays = [
        poetry2nix.overlay
        pyk.overlay
        (final: prev: {
          kmir-pyk = prev.poetry2nix.mkPoetryApplication {
            python = prev.python310;
            projectDir = ./kmir;
            overrides = prev.poetry2nix.overrides.withoutDefaults
              (finalPython: prevPython: { 
                pyk = prev.pyk-python310; 
                # exceptiongroup = prevPython.exceptiongroup.overridePythonAttrs (old: {
                #   propagatedBuildInputs = (old.propagatedBuildInputs or [ ]) ++ [ finalPython.flit-scm ];
                # });
                # filelock = prevPython.filelock.overridePythonAttrs (old: {
                #   propagatedBuildInputs = (old.propagatedBuildInputs or [ ]) ++ [ finalPython.hatchling ];
                # });
                # iniconfig = prevPython.iniconfig.overridePythonAttrs (old: {
                #   propagatedBuildInputs = (old.propagatedBuildInputs or [ ]) ++ [ finalPython.hatchling ];
                # });
                # packaging = prevPython.packaging.overridePythonAttrs (old: {
                #   propagatedBuildInputs = (old.propagatedBuildInputs or [ ]) ++ [ finalPython.flit-core ];
                # });
                # pathspec = prevPython.pathspec.overridePythonAttrs (old: {
                #   propagatedBuildInputs = (old.propagatedBuildInputs or [ ]) ++ [ finalPython.flit-core ];
                # });
                # pluggy = prevPython.pluggy.overridePythonAttrs (old: {
                #   propagatedBuildInputs = (old.propagatedBuildInputs or [ ]) ++ [ finalPython.setuptools ];
                # });
                # tomli = prevPython.tomli.overridePythonAttrs (old: {
                #   propagatedBuildInputs = (old.propagatedBuildInputs or [ ]) ++ [ finalPython.flit-core ];
                # });
                # typing-extensions = prevPython.typing-extensions.overridePythonAttrs (old: {
                #   propagatedBuildInputs = (old.propagatedBuildInputs or [ ]) ++ [ finalPython.flit-core ];
                # });
                # hatchling = prevPython.hatchling.overridePythonAttrs (old: {
                #   propagatedBuildInputs = (old.propagatedBuildInputs or [ ]) ++ [ finalPython.setuptools-scm ];
                # });
                }
              );
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
        };
      }) // {
        overlays.default = nixpkgs.lib.composeManyExtensions allOverlays;
      };
}
