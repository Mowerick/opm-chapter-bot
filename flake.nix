{
  description = "Simple Python 3 development environment with venv and pip support";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          pip
          requests
          numpy
        ]);
      in {
        devShells.default = pkgs.mkShell {
          name = "python-dev-shell";

          buildInputs = [ pythonEnv ];

          shellHook = ''
            echo "🐍 Python Dev Shell Ready"

            if [ ! -d ".venv" ]; then
              echo "📦 Creating virtual environment in .venv"
              python -m venv .venv
            fi

            source .venv/bin/activate
            echo "✅ .venv activated"
            echo "📦 Python version: $(python --version)"
            echo "📦 Pip location: $(which pip)"

            # Optional: Uncomment if you want IntelliJ to auto-start
            pycharm-professional . > /dev/null 2>&1 &
          '';
        };
      });
}
