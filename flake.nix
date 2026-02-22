{
  description =
    "Simple Python 3 development environment with venv and pip support";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        pythonEnv = pkgs.python3.withPackages (ps:
          with ps; [
            pip
            requests
            numpy
            pandas
            scikit-learn
            matplotlib
            joblib
            nbformat
            pandas-stubs
            notebook
          ]);
      in {
        packages.default = pkgs.buildEnv {
          name = "python-dev-env";
          paths = [ pythonEnv ];
        };

        devShells.default = pkgs.mkShell {
          name = "python-dev-shell";

          buildInputs = [ self.packages.${system}.default ];

          shellHook = ''
                echo "🐍 Python Dev Shell Ready"


                if [ -z "''${_IDE_LAUNCHED:-}" ]; then
                export _IDE_LAUNCHED=1
            	    nohup setsid pycharm-professional . >/dev/null 2>&1 < /dev/null &
            	  fi
          '';
        };
      });
}
