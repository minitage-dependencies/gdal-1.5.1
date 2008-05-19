import os
def getgdalenv(options,buildout):
    # copy in LNK_FLAGS for gdal < 1.5 !
    # see http://trac.osgeo.org/gdal/wiki/FAQInstallationAndBuilding#HowcaniaddparticularLDFLAGSwithGDAL1.5 (little hack (kiorky))
    os.environ['LNK_FLAGS'] = os.environ['LDFLAGS']
    os.environ['LIBS'] = os.environ['LDFLAGS']
# vim:set ts=4 sts=4 et  :
