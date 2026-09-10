# test execution (called in builder_cmd)
# Entry_CMD.exe --input-path "S:\\Coding\\Ab- LeRe\\MCWiiU-Texture-Builder\\MCLCE Texture Builder - Standalone\\test_data\\1.17_java" --input-path-type folder --input-game java --input-version 1.17 --output-path "S:\\Coding\\Ab- LeRe\\MCWiiU-Texture-Builder\\MCLCE Texture Builder - Standalone\\output" --output-structure "wiiu dump"

# default settings & package enforcement
from xLPyBasics.PathAPI import Path
from xLPyBasics import Dependencies
if not Dependencies.is_frozen():
    Dependencies.enforce_proj(Path.get_meipassp(Path.cwd()))
Path.default_prepension.set(Path.cwd())

# multithreading block
import InterfaceLibs.Interface as Interface
import multiprocessing
if __name__ == "__main__":
    multiprocessing.freeze_support() # stops pyinstaller multithreading looping

    # ║ use args to create an entrypoint
    # 〡 define args & get args
    from argparse import ArgumentParser, BooleanOptionalAction
    parser = ArgumentParser()
    parser.add_argument("--error-mode", type=str, default="replace")
    parser.add_argument("--processing-size", type=int, default=16)
    parser.add_argument("--input-path", type=str, required=True)
    parser.add_argument("--input-path-type", type=str, required=True)
    parser.add_argument("--input-game", type=str, required=True)
    parser.add_argument("--input-version", type=str, required=True)
    parser.add_argument("--output-path", type=str, required=True)
    parser.add_argument("--output-structure", type=str, required=True)
    parser.add_argument("--output-drive", type=str, default="system")
    parser.add_argument("--use-simple-processing", action=BooleanOptionalAction, default=False)
    parser.add_argument("--use-error-texture", action=BooleanOptionalAction, default=False)
    parser.add_argument("--main-loc", type=str, default="")
    parser.add_argument("--is-direct-path", action=BooleanOptionalAction, default=False)
    parser.add_argument("--force-dump-mode", action=BooleanOptionalAction, default=False)
    args = parser.parse_args()

    # create entrypoint and start
    from TextureLibs.EntryPoint import EntryPoint
    from CodeLibs import Logger as log
    entry = EntryPoint(
        args.error_mode,
        args.processing_size,

        args.input_path,
        args.input_path_type,
        args.input_game,
        args.input_version,

        args.output_path,
        args.output_structure,
        args.output_drive,

        (not args.use_simple_processing),
        args.use_error_texture,
        args.main_loc,
        log.LoggerHandler.DEFAULT_FLAGS,
        args.is_direct_path,
        args.force_dump_mode
    )
    entry.start()
