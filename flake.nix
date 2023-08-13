{
  description = " A flake for KMIR Semantics";

  inputs = {
    nixpkgs.url =
      "github:NixOS/nixpkgs/f971f35f7d79c53a83c7b10de953f1db032cba0e";
    k-framework.url = "github:runtimeverification/k/v6.0.44";
    flake-utils.follows = "k-framework/flake-utils";
    rv-utils.url = "github:runtimeverification/rv-nix-tools";
    poetry2nix.url = "github:nix-community/poetry2nix/master";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
    pyk.url = "github:runtimeverification/pyk/v0.1.401";
    pyk.inputs.flake-utils.follows = "k-framework/flake-utils";
    pyk.inputs.nixpkgs.follows = "k-framework/nixpkgs";
  };
  outputs =
    { self, k-framework, nixpkgs, flake-utils, poetry2nix, rv-utils, pyk }:
    let
      allOverlays = [
        poetry2nix.overlay
        pyk.overlay
        (final: prev: {
          kmir = prev.poetry2nix.mkPoetryApplication {
            python = final.python310;
            projectDir = ./kmir;
            overrides = prev.poetry2nix.overrides.withDefaults
              (finalPython: prevPython: {
                pyk = prev.pyk-python310.overridePythonAttrs (old: {
                  # both kmir and pyk depend on the filelock package, however the two packages are likely 
                  # to use different versions, based on whatever version was locked in their respecitve poetry.lock
                  # files. However, because all python package deps are propagated py poetry2nix into any
                  # subsequent packages that depend on them, we get a clash when two versions of the same package occur. 
                  # Below, we manually filter out the filelock package locked by pyk's poetry.lock file
                  # and substitute in the version from mir's poetry.lock.
                  # This is not ideal and may not be feasible if there are more/more complex clashes.
                  # We could just let poetry2nix download pyk without importing it as a flake,
                  # but then we would lose the ability to do kup install kmir --override pyk <version>
                  # and we would instead have to modify pyproject.toml to point to the version of pyk we want, then
                  # call kup install kmir --version . to use the modified local checkout.
                  propagatedBuildInputs = prev.lib.filter
                    (x: !(prev.lib.strings.hasInfix "filelock" x.name))
                    old.propagatedBuildInputs ++ [ finalPython.filelock ];
                });
              });
            groups = [ ];
            # We remove `dev` from `checkGroups`, so that poetry2nix does not try to resolve dev dependencies.
            checkGroups = [ ];
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
          inherit (pkgs) kmir;
          default = kmir;
          #  = pkgs..pyk;
        };
      }) // {
        overlays.default = nixpkgs.lib.composeManyExtensions allOverlays;
      };
}
