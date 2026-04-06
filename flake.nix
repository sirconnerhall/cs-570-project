{
  description = "CS 570 Assignment";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    with flake-utils.lib;
    eachSystem allSystems (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        tex = pkgs.texlive.combine {
          inherit (pkgs.texlive)
            scheme-basic
            latex-bin
            latexmk
            luaotfload
            cite
            amsmath
            amsfonts
            algorithms
            epstopdf
            xcolor
            metafont
            collection-fontsrecommended
            titlesec
            listings
            ;
        };
      in
      rec {
        packages = {
          document = pkgs.stdenvNoCC.mkDerivation rec {
            name = "570-1";
            src = self;
            buildInputs = [
              pkgs.coreutils
              tex
            ];
            phases = [
              "unpackPhase"
              "buildPhase"
              "installPhase"
            ];
            buildPhase = ''
              export PATH="${pkgs.lib.makeBinPath buildInputs}";
              mkdir -p . cache/texmf-var
              export TEXMFHOME=.cache
              export TEXMFVAR=.cache/texmf-var
              export TEXMFCACHE=.cache
              export SOURCE_DATE_EPOCH=${toString self.lastModified}
              latexmk -interaction=nonstopmode -pdf -lualatex \
              document.tex
            '';
            installPhase = ''
              mkdir -p $out
              cp document.pdf $out/
            '';
          };
        };
        defaultPackage = packages.document;
      }
    );
}
