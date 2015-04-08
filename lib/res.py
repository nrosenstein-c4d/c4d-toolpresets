# Automatically generated using nr.c4d.dev
# https://github.com/NiklasRosenstein/nr.c4d.dev

import os
import sys
import c4d

project_path = os.path.dirname(sys._getframe().f_back.f_globals['__file__'])
resource = sys._getframe().f_back.f_globals['__res__']


def string(name, *subst):
    result = resource.LoadString(globals()[name])
    for item in subst:
        result = result.replace('#', item, 1)
    return result


def tup(name, *subst):
    return (globals()[name], string(name, *subst))


def file(*parts):
    return os.path.join(project_path, *parts)


def bitmap(*parts):
    bitmap = c4d.bitmaps.BaseBitmap()
    result, ismovie = bitmap.InitWith(file(*parts))
    if result != c4d.IMAGERESULT_OK:
        return None
    return bitmap


IDS_TOOLPRESETS                = 0
IDS_TOOLPRESETS_HELP           = 1
IDS_MISSING_FILE               = 2
IDS_PRESET                     = 3
IDC_FOLDER                     = 4
IDC_TOOLNOTSUPPORTED           = 5
IDC_UNKOWNTOOL                 = 6
IDS_ERROR_FILENOTOPENED        = 7
IDS_ERROR_ACCESSDENIED         = 8
IDS_ERROR_NAMEEMPTY            = 9
IDC_ERROR_RENAMEFAILED         = 10
IDC_ERROR_FOLDERCREATIONFAILED = 11
IDC_ERROR_FOLDEREXISTS         = 12
IDC_ERROR_PRESETSNOTREMOVED    = 13
IDC_ASK_REMOVEALL              = 14
IDC_ASK_REMOVENODE             = 15
IDC_ASK_REMOVENODE_MULTIPLE    = 16
CONTEXT_NEWFOLDER              = 17
CONTEXT_OPEN                   = 18
TREEVIEW                       = 19
COLUMN_MAIN                    = 20
BMPB_SAVE                      = 21
BMPB_RELOAD                    = 22
STR_TOOL                       = 23
BMPB_TOOL                      = 24
GRP_MAIN                       = 25
GRP_TOOL                       = 26
CHK_ALL                        = 27

