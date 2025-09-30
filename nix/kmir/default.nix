{
  lib,
  stdenv,
  runCommand,
  makeWrapper,
  callPackage,

  k,
  which,
  stable-mir-json,
  stable-mir-json-rust,

  kmir-pyk,
  rev ? null,
  kmir-rust ? null,
}@args:

stdenv.mkDerivation {
  pname = "kmir";
  version = if (rev != null) then rev else "dirty";
  nativeBuildInputs = [
    k
    kmir-pyk
    makeWrapper
  ];

  src = callPackage ../kmir-source { };

  dontUseCmakeConfigure = true;

  enableParallelBuilding = true;

  buildPhase = ''
    export XDG_CACHE_HOME=$(pwd)
    kmir-kdist -v build -j4
  '';

  installPhase = ''
    mkdir -p $out
    cp -r ./kdist-*/* $out/
    mkdir -p $out/bin
    makeWrapper ${kmir-pyk}/bin/kmir $out/bin/kmir --prefix PATH : ${
      lib.makeBinPath (
        [
          which
          k
          stable-mir-json
        ]
        ++ lib.optionals (kmir-rust != null) [ kmir-rust ]
      )
    } --set KDIST_DIR $out
  '';

  passthru =
    if kmir-rust == null then
      {
        # list all supported solc versions here
        rust = callPackage ./default.nix (args // { kmir-rust = stable-mir-json-rust; });
      }
    else
      { };
}
