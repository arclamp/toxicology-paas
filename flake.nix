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
        ];
        shellHook = ''
          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [pkgs.stdenv.cc.cc]}:$LD_LIBRARY_PATH
        '';
      };
  };
}
