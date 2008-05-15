import os
import zc.buildout

from minitage.core.common import append_env_var

os_ldflags=''
uname=os.uname()[0]
if uname == 'Darwin':
    os_ldflags=' -mmacosx-version-min=10.5.0'

def post_make(options, buildout):
    """Custom post-make hook for bulding GDAL python bindings."""
    # Generate rpath information..
    rpath = ['%s/lib' % buildout[part]['location']
             for part
             in ('geos', 'proj', 'postgresql', 'libidn',
                 'libpng', 'libtiff', 'libgif',
                 'libjpeg', 'curl', 'zlib'
                 'libiconv', 'openssl', 'swig')
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

def getgdalenv(options,buildout):
    for var in ['zlib', 'libiconv', 'openssl', 'libidn',
                'geos', 'proj', 'swig', 'libtiff',
                'libjpeg', 'libtiff', 'libpng',
                'libgif', 'postgresql', 'postgis']:
        append_env_var('LDFLAGS',
                       ["-L%(lib)s/lib -Wl,-rpath -Wl,%(lib)s/lib %(os)s" %
                         {'lib': buildout[var]['location'],
                          'os':os_ldflags
                         }
                       ],
                       sep=' ',
                       before=False
                      )
        append_env_var('LD_RUN_PATH',
                       ["%(lib)s/lib'" % {
                           'lib':buildout[var]['location']
                       }
                       ],
                       sep=':',
                       before=False
                      )
        append_env_var('CFLAGS',
                       ["-I%s/include " %
                        (buildout[var]['location'])
                       ],
                       sep=' ',
                       before=False
                      )

    append_env_var('CFLAGS',
                   ["-I%s/include/openssl " %
                    (buildout['openssl']['location'])
                   ],
                   sep=' ',
                   before=False
                  )
    os.environ['CPPFLAGS'] = os.environ['CFLAGS']
    os.environ['CXXFLAGS'] = os.environ['CFLAGS']
    # copy in LNK_FLAGS for gdal < 1.5 !
    # see http://trac.osgeo.org/gdal/wiki/FAQInstallationAndBuilding#HowcaniaddparticularLDFLAGSwithGDAL1.5 (little hack (kiorky))
    os.environ['LNK_FLAGS'] = os.environ['LDFLAGS']
    os.environ['LIBS'] = os.environ['LDFLAGS']

# vim:set ts=4 sts=4 et  :
