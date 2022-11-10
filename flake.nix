{
  description = "A very basic flake";

  outputs = { self, nixpkgs }: {
    devShell.x86_64-linux =
      let
        pkgs = nixpkgs.legacyPackages.x86_64-linux;
      in
        pkgs.mkShell {
        buildInputs = [
          pkgs.python310Packages.virtualenv
          pkgs.autoPatchelfHook
        ];
        propagatedBuildInputs = [
          pkgs.stdenv.cc.cc.lib
          pkgs.zlib
        ];
        shellHook = ''
          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [pkgs.stdenv.cc.cc pkgs.zlib]}:$LD_LIBRARY_PATH
        '';
      };
  };
}
