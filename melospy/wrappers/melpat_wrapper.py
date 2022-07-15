from melospy.basic_representations.jm_util import string_to_dict
from melospy.tools.commandline_tools.param_helper import ParameterContainer


def define_melpat_params():
    # main
    main_params = ParameterContainer("main")
    main_params.add_param(name="audio_slicer", argname="audio_slicer",
                          confname="audio_slicer", defvalue=None)
    main_params.add_param(name="beatometer", argname="",
                          confname="beatometer", defvalue={})
    main_params.add_param(name="convention", argname="convention",
                          confname="convention",
                          defvalue="en", post_process=lambda x: x[0] if isinstance(x, list) else x)
    main_params.add_param(name="crop_images", argname="crop_images",
                          confname="crop_images",
                          defvalue=False)
    main_params.add_param(name="flexq", argname="",
                          confname="flexq", defvalue={})
    main_params.add_param(name="krn_reader", argname="",
                          confname="krn_reader", defvalue={})
    main_params.add_param(name="maxN", argname="maxN", confname="maxN",
                          defvalue=30, post_process=lambda x: x[0] if isinstance(x, list) else x)
    main_params.add_param(name="mcsv_reader", argname="",
                          confname="mcsv_reader", defvalue={})
    main_params.add_param(name="melody_importer", argname="",
                          confname="melody_importer", defvalue={})
    main_params.add_param(name="midi_reader", argname="",
                          confname="midi_reader", defvalue={})
    main_params.add_param(name="outdir", argname="outdir", confname="outdir",
                          defvalue=".", post_process=lambda x: x[0] if isinstance(x, list) else x)
    main_params.add_param(name="outfile", argname="positional",
                          confname="outfile",
                          defvalue="pattern.csv", post_process=lambda x: x[0] if isinstance(x, list) else x)
    main_params.add_param(name="precision", argname="precision",
                          confname="precision",
                          defvalue=3, post_process=lambda x: int(x[0]) if isinstance(x, list) else int(x))
    main_params.add_param(name="requests", argname="request",
                          confname="requests", defvalue=[], post_process=string_to_dict)
    main_params.add_param(name="sv_reader", argname="",
                          confname="sv_reader", defvalue={})
    main_params.add_param(name="tunes", argname="input", confname="tunes",
                          defvalue=[], post_process=lambda x: x if isinstance(x[0], dict) else [{"file": k} for k in x])
    main_params.add_param(name="verbose", argname="verbose",
                          confname="verbose",
                          defvalue=False,
                          post_process=lambda x: bool(x[0]) if isinstance(x, list) else bool(x))
    main_params.add_param(name="wdir", argname="dir", priority="conf",
                          confname="dir",
                          defvalue=".", post_process=lambda x: x[0] if isinstance(x, list) else x)
    main_params.add_param(name="app_name", argname="app_name", confname="app_name", defvalue=None)

    # db
    db_params = ParameterContainer("db")
    db_params.add_param(name="content_type", argname="", confname="database:content_type",
                        defvalue="sv", post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="path", argname="db_path", confname="database:path",
                        defvalue="", post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="pwd", argname="db_pwd", confname="database:password",
                        defvalue="", post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="type", argname="db_type", confname="database:type",
                        defvalue="", post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="use", argname="", confname="database:use", defvalue=False, post_process=lambda x: len(
        x[0]) > 0 if isinstance(x, list) else len(x) > 0 if isinstance(x, str) else x)
    db_params.add_param(name="user", argname="db_user", confname="database:user",
                        defvalue="", post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="session", argname="db_session", confname="database:session",
                        defvalue=None)

    # dir_paths
    dir_paths_params = ParameterContainer("dir_paths")
    dir_paths_params.add_param(name="outdir", argname="outdir", confname="outdir",
                               defvalue=".", post_process=lambda x: x[0] if isinstance(x, list) else x)
    dir_paths_params.add_param(name="wdir", argname="dir", priority="conf", confname="dir",
                               defvalue=".", post_process=lambda x: x[0] if isinstance(x, list) else x)

    return main_params, db_params, dir_paths_params
