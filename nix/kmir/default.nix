{
  lib,
  stdenv,
  runCommand,
  makeWrapper,
  callPackage,

  k,
  which,
  stable-mir-json,

  kmir-pyk,
  rev ? null
} @ args:

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
      lib.makeBinPath [
        which
        k
        stable-mir-json
      ]
    } --set KDIST_DIR $out
  '';
}