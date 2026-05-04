import os
import subprocess
import sys
import platform

if platform.system() == "Darwin":
    env_script_path = "/Applications/Tecplot 360 EX 2025 R2/bin/tec360-env"
elif platform.system() == "Linux":
    env_script_path = "/most/common/path..."

FLAG = "__IN_ENV__"

def in_env():
    return os.environ.get(FLAG) == "1"

if not in_env() and platform.system() != "Windows":
    # Relaunches THIS file, but with the flag __IN_ENV__ set.
    # All output *should* be piped to the same terminal
    subprocess.run(
        [env_script_path, 
         "--", 
         sys.executable, # using this rather than just 'python' ensures the same python interpreter
         __file__] + sys.argv[1:],
        env={**os.environ, FLAG: "1"}, # run with flag set
        check=True,
    )
    raise sys.exit()

# --- all code goes here and runs "inside" the env ---
import tecplot as tp

tp.new_layout()
ds = tp.active_frame().dataset
print(ds)
print("\nSuccessfully called batch mode without setting env in shell!\n")





