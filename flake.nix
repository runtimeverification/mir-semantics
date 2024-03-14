{
  description = " A flake for KMIR Semantics";

  inputs = {
    k-framework.url = "github:runtimeverification/k/v6.3.39";
    nixpkgs.follows = "k-framework/nixpkgs";
    flake-utils.follows = "k-framework/flake-utils";
    rv-utils.follows = "k-framework/rv-utils";
    pyk.url = "github:runtimeverification/pyk/v0.1.712";
    nixpkgs-pyk.follows = "pyk/nixpkgs";
    poetry2nix.follows = "pyk/poetry2nix";
  };
  outputs =
    { self, k-framework, nixpkgs, flake-utils, rv-utils, pyk, ... }@inputs:
    let
      overlay = (final: prev:
        let
          nixpkgs-pyk = import inputs.nixpkgs-pyk {
            system = prev.system;
            overlays = [ pyk.overlay ];
          };
          poetry2nix =
            inputs.poetry2nix.lib.mkPoetry2Nix { pkgs = nixpkgs-pyk; };
          k_release = builtins.readFile ./deps/k_release;
        in {
          kmir-pyk = poetry2nix.mkPoetryApplication {
            python = nixpkgs-pyk.python310;
            projectDir = ./kmir;
            overrides = poetry2nix.overrides.withDefaults
              (finalPython: prevPython: {
                pyk = nixpkgs-pyk.pyk-python310.overridePythonAttrs (old: {
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

          kmir = prev.stdenv.mkDerivation {
            pname = "kmir";
            version = self.rev or "dirty";
            buildInputs = with prev; [
              k-framework.packages.${prev.system}.k
              final.kmir-pyk
            ];
            nativeBuildInputs = [ prev.makeWrapper ];

            src = ./kmir;

            # kmir init $(kbuild which llvm) is to populate $out/lib/llvm
            # with parser_Mir_MIR-SYNTAX from gen_glr_parser 
            # before nix directory becomes read only
            buildPhase = ''
              export KBUILD_DIR=".kbuild"
              patchShebangs .
              make build-backends VERSION="${k_release}" POETRY_RUN=
            '';

            # Now mir-semantics is built, wrap kmir with LLVM and HASKELL defs
            installPhase = ''
              mkdir -p $out/lib/
              cp -r $(kbuild which llvm) $out/lib/
              cp -r $(kbuild which haskell) $out/lib/ 

              mkdir -p $out/bin/

              makeWrapper ${final.kmir-pyk}/bin/kmir $out/bin/kmir \
                --set KMIR_LLVM_DIR "$out/lib/llvm" \
                --set KMIR_HASKELL_DIR "$out/lib/haskell" \
                --prefix PATH : ${
                  prev.lib.makeBinPath [ k-framework.packages.${prev.system}.k ]
                }
            '';
          };

          kmir-test = prev.stdenv.mkDerivation {
            pname = "kmir-test";
            version = self.rev or "dirty";

            src = ./.;

            buildInputs = [ final.kmir prev.which prev.git ];

            buildPhase = ''
              mkdir -p tests/
              cp -v kmir/src/tests/integration/test-data/run-rs/functions/sum-to-n.* tests/
              cp -v kmir/src/tests/nix/sum-to-n.* tests/
              cp -v kmir/src/tests/integration/test-data/prove-rs/verify.k tests/
              cp -v kmir/src/tests/integration/test-data/prove-rs/simple-spec.k tests/
              cp -v kmir/src/tests/nix/nix-tests.sh tests/
              cd tests/
              sed -i 's!requires "../../../../../k-src/mir.md"!requires "../kmir/k-src/mir.md"!' verify.k
              patchShebangs .
              ./nix-tests.sh
            '';

            installPhase = ''
              touch $out
            '';
          };
        });
    in flake-utils.lib.eachSystem [
      "x86_64-linux"
      "x86_64-darwin"
      "aarch64-linux"
      "aarch64-darwin"
    ] (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ overlay ];
        };
      in {
        packages = rec {
          inherit (pkgs) kmir kmir-test;
          default = kmir;
        };
      }) // {
        overlays.default = overlay;
      };
}
