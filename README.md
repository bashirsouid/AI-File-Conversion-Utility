# AI-File-Conversion-Utility

A command line utility written in Python that will recursively modify matching files in a directory according to instructions from an AI prompt.

## Project Status

In development early. Not yet ready for usage. Ready to begin testing and bug fixing.

I tried generating some unit tests and integration tests with AI but they aren't good; I will have to write them from scratch later.

## Build Instructions
- Startup a virtual environment with `setup_env.py.run`.
- Activate the virtual environment with `source ./venv/bin/activate`.
- Build the Python project as a single executable with `build.sh`.

## Installation Instructions
- Copy the binary from `dist/modify` to your PATH.
- Setup your `.modify.env` file according to the example in the same PATH directory as the binary.

## Run Instructions
1. Execute the executable from any directory to create a sample config file for you; or author it yourself from scratch if you prefer. It will look something like the following:

```json
{
    "file_extension": ".json",
    "output_suffix": ".converted",
    "replace_original": false,
    "prompt_file": null,
    "prompt_text": "Go line by line and capitalize all of the letters on that line.",
}
```

2. Run the script with a valid configuration file `modify --config ./config.json ./`.

## Config File Format
- The `file_extension` field will specify which file extension should be used when searching for files in the directory tree to convert.
- If the prompt-file is specified, then it will be used. Otherwise, it will use the prompt text.
- If you replace the original files, a backup will be made for the originals with `.bak` appended to the filename.
- Whether or not the original files will be replaced, the converted files will be stored as `<original_filename>.converted.<original_extension>` or whatever suffix you specify in the `output_suffix` variable value.

## Tips:

### Isolate file output
If you are having a lot of issues with the LLM adding extra content, then try a prompt like this that repeats the instructions multiple times. Unfortunately, the LLM providers themselves work very very hard to make models that think out loud so you can check their work. That is good for building user trust, but sucks for file conversion utilities.

```
Go line by line of the file and capitalize all of the chracters.

Just return the final text by itself; do NOT include any additional commentary or explaination before or afterwards.
Do NOT explain your thought proccess at ALL; just return the final file contents without repeating my input or explaining anything!
I WANT YOU TO NOT RETURN ANYTHING MORE THAN THE FINAL FILE CONTENTS!
```

## TODO
- [ ] Complete development for script & testing
- [ ] Support configurable recursive option
- [ ] Unit test suite
- [ ] Integration test suite
