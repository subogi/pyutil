import os, sys
import traceback

def parse_args(progName):
    import argparse
    parser = argparse.ArgumentParser(
        description=f'{progName} Process')
    parser.add_argument(
        '-c',
        '--config-file',
        type=str,
        default='config.yaml',
        help='Path to the config file')
    parser.add_argument(
        '-i',
        '--index',
        type=int,
        default=1,
        choices=[1, 2, 3, 4, 5],
        help='kafka index (1 ~ 5)')
    parser.add_argument(
        '-e',
        '--env',
        type=str,
        default="dev",
        choices=["dev", "stg", "prd"],
        help="Environment: dev, stg, or prd (optional)")
    parser.add_argument(
        '-u',
        '--update-flag',
        type=bool,
        choices=[True,False],
        default=True,
        help="Kafka Offset Update Flag (deafult:True)")
    parser.add_argument(
        '-o',
        '--offset-option', # false:latest, true:earliest (default=true)
        type=int,
        default=1,
        help="Kafka Offset Consumption Flag (deafult:earliest(1), latest(0))")
    if len(sys.argv) == 1:
        parser.print_help()

    return parser.parse_args()

def configure(cfgfile):
    try:
        from cfg_util import Config
        data_type = None
        if os.path.splitext(cfgfile)[-1] == '.yaml':
            data_type = 'yaml'
        elif os.path.splitext(cfgfile)[-1] == '.json':
            data_type = 'json'
        else:
            raise Exception(f"Only JSON and YAML files are supported. your config file is ({cfgfile})")
        config = Config(data_type=data_type, file_class="file", config_datas=cfgfile)
        return True, config
    except Exception as e:
        print(f'configure error\n{traceback.format_exc()}')
        return False, e


    return config
if __name__ == '__main__':
    from log_util import Log
    # config load
    prog_name = 'test'
    args = parse_args(prog_name)
    ret, cfg = configure(args.config_file)
    if not ret :
        exit(f"configure failed. ({cfg})")

    # log init
    logopts = cfg.GetConfigData("LOG")
    log = Log()
    if log.OpenLog(prog_name, logopts) :
        log.info_log('set log success!')

