from melospy.tools.commandline_tools.param_helper import ParameterContainer


def define_melconv_params():
    # main
    main_params = ParameterContainer("main")
    main_params.add_param(name="bundles", argname="input", confname="bundles", defvalue=[], post_process=lambda x: x if isinstance(x[0], dict) else [{"file":x[0]}] )
    main_params.add_param(name="flexq", argname="", confname="flexq", defvalue={} )
    main_params.add_param(name="mcsv_reader", argname="", confname="mcsv_reader", defvalue={} )
    main_params.add_param(name="sv_reader", argname="", confname="sv_reader", defvalue={} )
    main_params.add_param(name="krn_reader", argname="", confname="krn_reader", defvalue={} )
    main_params.add_param(name="beatometer", argname="", confname="beatometer", defvalue={} )
    main_params.add_param(name="midi_reader", argname="", confname="midi_reader", defvalue={} )
    main_params.add_param(name="wdir", argname="dirmcsv", priority="conf", confname="dir", defvalue=".", post_process=lambda x: x[0] if isinstance(x, list) else x)
    main_params.add_param(name="outdir", argname="outdir", confname="outdir", defvalue=".", post_process=lambda x: x[0] if isinstance(x, list) else x)
    main_params.add_param(name="output_format", argname="format", confname="output:format", defvalue=".", post_process=lambda x: x[0] if isinstance(x, list) else x)
    main_params.add_param(name="input_format", argname="inputformat", confname="input_format", defvalue=None, post_process=lambda x: x[0] if isinstance(x, list) else x)
    main_params.add_param(name="transpose", argname="transpose", confname="output:transpose", defvalue=0, post_process=lambda x: int(x[0]) if isinstance(x, list) else int(x))
    main_params.add_param(name="verbose", argname="verbose", confname="verbose", defvalue=False, post_process=lambda x: bool(x[0]) if isinstance(x, list) else bool(x))
    main_params.add_param(name="sink_dbi", argname="", confname="sinkdatabase", defvalue={}, post_process=lambda x: x[0] if isinstance(x, list) else x)
    main_params.add_param(name="output_params", argname="", confname="output", defvalue={})
    main_params.add_param(name="melody_importer", argname="", confname="melody_importer", defvalue={})

    # db
    db_params = ParameterContainer("src_dbi")
    db_params.add_param(name="type", argname="dbtype", confname="srcdatabase:type", defvalue="", post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="path", argname="dbpath", confname="srcdatabase:path", defvalue="", post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="user", argname="dbuser", confname="srcdatabase:user", defvalue="", post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="pwd", argname="dbpwd", confname="srcdatabase:password", defvalue="", post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="rebuild", argname="dbrebuild", confname="srcdatabase:rebuild", defvalue=False, post_process=lambda x: x[0] if isinstance(x, list) else x)
    db_params.add_param(name="use", argname="dbpath", confname="srcdatabase:use", defvalue=False, post_process=lambda x: len(x[0])>0 if isinstance(x, list) else len(x)>0 if isinstance(x, str) else x)
    db_params.add_param(name="version", argname="dbversion", confname="srcdatabase:version", defvalue=False, post_process=lambda x: len(x[0])>0 if isinstance(x, list) else len(x)>0 if isinstance(x, str) else x)
    db_params.add_param(name="content_type",  argname="", confname="srcdatabase:content_type",  defvalue="sv", post_process=lambda x: x[0] if isinstance(x, list) else x)

    # dir_paths
    dir_paths_params = ParameterContainer("dir_paths")
    dir_paths_params.add_param(name="wdir", argname="dir", priority="conf", confname="dir", defvalue=".", post_process=lambda x: x[0] if isinstance(x, list) else x)
    dir_paths_params.add_param(name="outdir", argname="outdir", confname="outdir", defvalue=".", post_process=lambda x: x[0] if isinstance(x, list) else x)

    return main_params, db_params, dir_paths_params
