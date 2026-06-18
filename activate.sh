# Activate the Python environment that has PyAutoLens installed.
#
# Most users just `pip install autolens` (see the al_setup_environment skill) into a
# virtual environment. By default this looks for a `.venv` created inside the project
# (what al_setup_environment makes); edit VENV to point elsewhere, e.g. ~/venv/PyAuto.
#
# Resolving relative to this file (not the current directory) means it works both for a
# local `source activate.sh` and for the HPC scripts' `source $PROJECT_PATH/activate.sh`.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV=$HERE/.venv

if [ -f "$VENV/bin/activate" ]; then
    source "$VENV/bin/activate"
elif [ -n "${PYAUTO_HPC_BASE:-}" ] && [ -f "$PYAUTO_HPC_BASE/PyAuto/bin/activate" ]; then
    # Shared / HPC checkout: point PYAUTO_HPC_BASE at the directory that holds a
    # `PyAuto/` virtualenv alongside editable PyAuto* source checkouts, e.g.
    #   export PYAUTO_HPC_BASE=/path/to/your/PyAuto
    BASE="$PYAUTO_HPC_BASE"
    source "$BASE/PyAuto/bin/activate"
    export PYTHONPATH=$BASE:\
$BASE/PyAutoConf:\
$BASE/PyAutoFit:\
$BASE/PyAutoArray:\
$BASE/PyAutoGalaxy:\
$BASE/PyAutoLens
else
    echo "No local .venv found (set PYAUTO_HPC_BASE for a shared/HPC PyAuto checkout)." >&2
fi

# Developer setup only: if you run against editable source checkouts of the PyAuto*
# libraries instead of a pip install, drop the line above and add their parent directory
# to PYTHONPATH, e.g.:
#
#   SRC=~/Code/PyAutoLabs
#   export PYTHONPATH=$SRC:\
#   $SRC/PyAutoConf:\
#   $SRC/PyAutoFit:\
#   $SRC/PyAutoArray:\
#   $SRC/PyAutoGalaxy:\
#   $SRC/PyAutoLens
