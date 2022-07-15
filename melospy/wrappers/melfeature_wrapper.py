from melospy.basic_representations.jm_util import string_to_dict
from melospy.tools.commandline_tools.param_helper import ParameterContainer


def define_melfeature_params():
    # main
    main_params = ParameterContainer("main", case_sensitive = True)
    main_params.add_param(name="tunes", argname="svfile", confname="tunes", defvalue=[], post_process=lambda x: x if isinstance(x[0], dict) else [{"file":k} for k in x] )
    main_params.add_param(name="cma", argname="", confname="metrical_annotation_params", defvalue={} )
    main_params.add_param(name="outfile", argname="positional", confname="outfile", defvalue="features.csv", post_process=lambda x: x[0] if isinstance(x, list) else x)
    main_params.add_param(name="verbose", argname="verbose", confname="verbose", defvalue=False, post_process=lambda x: bool(x[0]) if isinstance(x, list) else bool(x))
    main_params.add_param(name="shortnames", argname="shortnames", confname="shortnames", defvalue=False, post_process=lambda x: bool(x[0]) if isinstance(x, list) else bool(x))
    main_params.add_param(name="split_ids", argname="", confname="split_ids", defvalue=True, post_process=lambda x: bool(x[0]) if isinstance(x, list) else bool(x))
    main_params.add_param(name="wide_format", argname="", confname="wide_format", defvalue=False, post_process=lambda x: bool(x[0]) if isinstance(x, list) else bool(x))
    main_params.add_param(name="convention", argname="convention", confname="convention", defvalue="English", post_process=lambda x: x[0] if isinstance(x, list) else x)
    main_params.add_param(name="NA_str", argname="na_str", confname="NA_str", defvalue="NA", post_process=lambda x: x[0] if isinstance(x, list) else x)
    main_params.add_param(name="precision", argname="", confname="precision", defvalue=2, post_process=lambda x: int(x[0]) if isinstance(x, list) else int(x))
    main_params.add_param(name="features", argname="feature", confname="features", defvalue=[], post_process=string_to_dict)
    main_params.add_param(name="segmentations", argname="segmentation", confname="segments", defvalue=[], post_process=string_to_dict)
    main_params.add_param(name="melvisParams", argname="", confname="melvis", defvalue=None, post_process=lambda x: x)
    main_params.add_param(name="flexq", argname="", confname="flexq", defvalue={} )
    main_params.add_param(name="mcsv_reader", argname="", confname="mcsv_reader", defvalue={} )
    main_params.add_param(name="sv_reader", argname="", confname="sv_reader", defvalue={} )
    main_params.add_param(name="beatometer", argname="", confname="beatometer", defvalue={} )
    main_params.add_param(name="midi_reader", argname="", confname="midi_reader", defvalue={} )
    main_params.add_param(name="krn_reader", argname="", confname="krn_reader", defvalue={} )
    main_params.add_param(name="melody_importer", argname="", confname="melody_importer", defvalue={} )

    # db
    db_params = ParameterContainer("src_dbi")
    db_params.add_param(name="type", argname="db_paramstype", confname="database:type", defvalue="", post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="path", argname="db_paramspath", confname="database:path", defvalue="", post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="user", argname="db_paramsuser", confname="database:user", defvalue="", post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="pwd", argname="db_paramspwd", confname="database:password", defvalue="", post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="use", argname="db_paramspath", confname="database:use", defvalue=False, post_process=lambda x: len(x[0])>0 if isinstance(x, list) else len(x)>0 if isinstance(x, str) else x)
    db_params.add_param(name="content_type",  argname="", confname="database:content_type",  defvalue="sv", post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="version",  argname="", confname="database:version",  defvalue=None, post_process=lambda x: x[0] if isinstance(x, list) else x)

    # dir_paths
    dir_paths_params = ParameterContainer("dir_paths_params")
    dir_paths_params.add_param(name="wdir", argname="dir", priority="conf", confname="dir", defvalue=".", post_process=lambda x: x[0] if isinstance(x, list) else x)
    dir_paths_params.add_param(name="outdir", argname="outdir", confname="outdir", defvalue=".", post_process=lambda x: x[0] if isinstance(x, list) else x)
    dir_paths_params.add_param(name="feature_dir", argname="feature_dir", confname="feature_dir", defvalue=".", post_process=lambda x: x[0] if isinstance(x, list) else x)

    return main_params, db_params, dir_paths_params
