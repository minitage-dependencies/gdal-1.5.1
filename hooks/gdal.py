import logging
import shutil
import os
import re
import zc.buildout

os_ldflags=''
uname=os.uname()[0]
if uname == 'Darwin':
    os_ldflags=' -mmacosx-version-min=10.5.0'

log = logging.getLogger('GDAL hook')
def substitute(filename, search_re, replacement):
    """Substitutes text within the contents of ``filename`` matching
    ``search_re`` with ``replacement``.
    """
    search = re.compile(search_re, re.MULTILINE)
    text = open(filename).read()
    text = replacement.join(search.split(text))

    newfilename = '%s%s' % (filename, '.~new')
    newfile = open(newfilename, 'w')
    newfile.write(text)
    newfile.close()
    shutil.copymode(filename, newfilename)
    shutil.move(newfilename, filename)

def post_make(options, buildout):
    """Custom post-make hook for bulding GDAL python bindings."""
    # Generate rpath information..
    rpath = ['%s/lib' % buildout[part]['location']
             for part
             in ('geos','proj','postgresql','libpng','libtiff','libgif','libjpeg','curl')
             ] + ['%s/lib' % options['location']]

    # ..and push it into the setup file
    substitute('setup.py',
               'extra_link_args=EXTRA_LINK_ARGS,',
               'extra_link_args=EXTRA_LINK_ARGS, runtime_library_dirs=%s' % str(rpath))

    cmd = '%s setup.py install' % buildout[buildout['buildout']['python']]['executable']
    log.info('Installing GDAL python bindings')

    if os.system(cmd):
        log.error('Error executing command: %s' % cmd)
        raise zc.buildout.UserError('System error')

def appendEnvVar(env,var,sep=":",before=True):
    """ append text to a environnement variable
    @param env String variable to set
    @param before append before or after the variable"""
    for path in var:
    	if before:os.environ[env] = "%s%s%s" % (path,sep,os.environ.get(env,''))
	else:os.environ[env] = "%s%s%s" % (os.environ.get(env,''),sep,path)

def getgdalenv(options,buildout):
    for var in ['zlib','libiconv','openssl','geos','proj','swig','libtiff','libjpeg', 'libtiff', 'libpng', 'libgif','postgresql','postgis']:
        appendEnvVar('LDFLAGS', ["-L%(lib)s/lib -Wl,-rpath -Wl,%(lib)s/lib %(os)s"%{'lib':buildout[var]['location'],'os':os_ldflags}],sep=' ',before=False)
        appendEnvVar('LD_RUN_PATH', ["%(lib)s/lib'"%{'lib':buildout[var]['location']}],sep=':',before=False)
        appendEnvVar('CFLAGS', ["-I%s/include "%(buildout[var]['location'])],sep=' ',before=False)

    appendEnvVar('CFLAGS', ["-I%s/include/openssl "%(buildout['openssl']['location'])],sep=' ',before=False)
    os.environ['CPPFLAGS'] = os.environ['CFLAGS']
    os.environ['CXXFLAGS'] = os.environ['CFLAGS']
    # copy in LNK_FLAGS for gdal < 1.5 !
    # see http://trac.osgeo.org/gdal/wiki/FAQInstallationAndBuilding#HowcaniaddparticularLDFLAGSwithGDAL1.5 (little hack (kiorky))
    os.environ['LNK_FLAGS'] = os.environ['LDFLAGS']
    os.environ['LIBS'] = os.environ['LDFLAGS']

# vim:set ts=4 sts=4 et  :
