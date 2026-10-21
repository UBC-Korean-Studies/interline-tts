{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  name = "interline-tts";

  packages = with pkgs; [
    python3
    ffmpeg
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${
      pkgs.lib.makeLibraryPath [
        pkgs.stdenv.cc.cc.lib
        pkgs.zlib
      ]
    }''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

    if [ ! -d .venv ]; then
      python -m venv .venv
    fi
    source .venv/bin/activate
    pip install -q -r requirements.txt
  '';
}
