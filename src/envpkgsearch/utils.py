# pyscan/utils.py
import subprocess
import sys
import os # Added os import for potential path checks in the future, though not strictly needed for current run_subprocess

def run_subprocess(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """
    Runs a subprocess command, handling common issues and ensuring consistent options.

    Args:
        cmd: A list of strings representing the command and its arguments
             (e.g., ['python', '-c', 'print("hello")']).
        **kwargs: Additional keyword arguments to pass directly to subprocess.run().
                  Common ones include:
                  - capture_output=True: Capture stdout and stderr.
                  - check=True: Raise CalledProcessError if the command returns a non-zero exit code.
                  - cwd: Set the current working directory for the command.
                  - env: Replace the environment variables for the command.
                  - timeout: Set a timeout for the command execution.

    Returns:
        A subprocess.CompletedProcess object containing stdout, stderr, returncode, etc.

    Raises:
        FileNotFoundError: If the executable specified in cmd[0] is not found.
        subprocess.CalledProcessError: If 'check=True' was passed in kwargs and the
                                       command returned a non-zero exit code.
        Exception: For other unexpected errors during subprocess execution.
    """
    # --- 1. Ensure Text Output and Encoding ---
    # This ensures stdout/stderr are returned as strings instead of bytes.
    # We prioritize text=True. If caller explicitly set it to False, we respect that.
    kwargs['text'] = kwargs.get('text', True)

    # Ensure an encoding is set if text=True, default to the system's default encoding
    # if not explicitly provided by the caller. UTF-8 is a common alternative.
    if kwargs.get('text') and 'encoding' not in kwargs:
         kwargs['encoding'] = sys.getdefaultencoding()
         # Alternative: kwargs['encoding'] = 'utf-8' # Often safer for portability

    # --- 2. Ensure shell=False for Safety ---
    # Running with shell=False is generally safer as it avoids invoking the system shell,
    # reducing the risk of shell injection if parts of the command come from user input.
    # It also means the first item in `cmd` is the exact executable path.
    # We force shell=False, as running with shell=True would change how `cmd` is interpreted.
    kwargs['shell'] = False

    # --- 3. Execute the Subprocess with Error Handling ---
    try:
        # This is the core call to the standard library function.
        # `**kwargs` unpacks our dictionary of arguments into keyword arguments
        # expected by subprocess.run().
        result = subprocess.run(cmd, **kwargs)

        # If check=True was in kwargs and the command failed, subprocess.run()
        # would raise subprocess.CalledProcessError right here.
        # If check=False, we would need to manually check result.returncode here
        # if we wanted to treat non-zero exit codes as errors.

        # Return the result object on success (or if check=False and command failed)
        return result

    except FileNotFoundError:
        # This specific error occurs if the executable cmd[0] cannot be found in the system's PATH
        # or at the specified absolute path. It's a common error, so we catch it explicitly
        # and re-raise it after potentially logging (though we just re-raise here).
        # Re-raising preserves the original exception traceback.
        raise

    except Exception as e:
        # This is a general catch-all for other unexpected errors during the process startup
        # or execution *before* a return code is generated (e.g., permission denied,
        # invalid arguments not caught earlier by Python, OS-level errors).
        # If check=True was used, CalledProcessError (a subclass of Exception) would also
        # be caught here if it wasn't caught explicitly before.
        print(f"Error running command: {' '.join(cmd)}", file=sys.stderr)
        print(f"Error details: {e}", file=sys.stderr)
        # Re-raise the original exception so the caller knows the command failed.
        raise