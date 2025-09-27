{
  stdenv,
  callPackage,

  which,

  kmir,
  rev ? null
}:

stdenv.mkDerivation {
  pname = "kmir-package-test";
  version = if (rev != null) then rev else "dirty";

  src = callPackage ../kmir-source { };

  enableParallelBuilding = true;

  nativeBuildInputs = [
    which
    kmir.rust
  ];

  # for package/test-package.sh
  postPatch = ''
    patchShebangs .
  '';

  buildPhase = ''
    runHook preBuild
    # cat package/test-package.sh
    # bash package/test-package.sh
    package/test-package.sh
    runHook postBuild
  '';

  installPhase = ''
    touch $out
  '';
}