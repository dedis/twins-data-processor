import tmtk

import json


def process():
    with open('config.json') as config_file:
        config = json.load(config_file)

    study = tmtk.Study(f'{config["input_directory"]}/study.params')

    export = tmtk.toolbox.SkinnyExport(study, config['output_directory'])
    export.to_disk()


if __name__ == '__main__':
    process()
