dnl config.m4 for extension jsonparser

dnl Comments in this file start with the string 'dnl'.
dnl Remove where necessary.

dnl If your extension references something external, use 'with':

dnl PHP_ARG_WITH([jsonparser],
dnl   [for jsonparser support],
dnl   [AS_HELP_STRING([--with-jsonparser],
dnl     [Include jsonparser support])])

dnl Otherwise use 'enable':

PHP_ARG_ENABLE([jsonparser],
  [whether to enable jsonparser support],
  [AS_HELP_STRING([--enable-jsonparser],
    [Enable jsonparser support])],
  [no])

if test "$PHP_JSONPARSER" != "no"; then
  dnl Write more examples of tests here...

  dnl Remove this code block if the library does not support pkg-config.
  dnl PKG_CHECK_MODULES([LIBFOO], [foo])
  dnl PHP_EVAL_INCLINE($LIBFOO_CFLAGS)
  dnl PHP_EVAL_LIBLINE($LIBFOO_LIBS, JSONPARSER_SHARED_LIBADD)

  dnl If you need to check for a particular library version using PKG_CHECK_MODULES,
  dnl you can use comparison operators. For example:
  dnl PKG_CHECK_MODULES([LIBFOO], [foo >= 1.2.3])
  dnl PKG_CHECK_MODULES([LIBFOO], [foo < 3.4])
  dnl PKG_CHECK_MODULES([LIBFOO], [foo = 1.2.3])

  dnl Remove this code block if the library supports pkg-config.
  dnl --with-jsonparser -> check with-path
  dnl SEARCH_PATH="/usr/local /usr"     # you might want to change this
  dnl SEARCH_FOR="/include/jsonparser.h"  # you most likely want to change this
  dnl if test -r $PHP_JSONPARSER/$SEARCH_FOR; then # path given as parameter
  dnl   JSONPARSER_DIR=$PHP_JSONPARSER
  dnl else # search default path list
  dnl   AC_MSG_CHECKING([for jsonparser files in default path])
  dnl   for i in $SEARCH_PATH ; do
  dnl     if test -r $i/$SEARCH_FOR; then
  dnl       JSONPARSER_DIR=$i
  dnl       AC_MSG_RESULT(found in $i)
  dnl     fi
  dnl   done
  dnl fi
  dnl
  dnl if test -z "$JSONPARSER_DIR"; then
  dnl   AC_MSG_RESULT([not found])
  dnl   AC_MSG_ERROR([Please reinstall the jsonparser distribution])
  dnl fi

  dnl Remove this code block if the library supports pkg-config.
  dnl --with-jsonparser -> add include path
  dnl PHP_ADD_INCLUDE($JSONPARSER_DIR/include)

  dnl Remove this code block if the library supports pkg-config.
  dnl --with-jsonparser -> check for lib and symbol presence
  dnl LIBNAME=JSONPARSER # you may want to change this
  dnl LIBSYMBOL=JSONPARSER # you most likely want to change this

  dnl If you need to check for a particular library function (e.g. a conditional
  dnl or version-dependent feature) and you are using pkg-config:
  dnl PHP_CHECK_LIBRARY($LIBNAME, $LIBSYMBOL,
  dnl [
  dnl   AC_DEFINE(HAVE_JSONPARSER_FEATURE, 1, [ ])
  dnl ],[
  dnl   AC_MSG_ERROR([FEATURE not supported by your jsonparser library.])
  dnl ], [
  dnl   $LIBFOO_LIBS
  dnl ])

  dnl If you need to check for a particular library function (e.g. a conditional
  dnl or version-dependent feature) and you are not using pkg-config:
  dnl PHP_CHECK_LIBRARY($LIBNAME, $LIBSYMBOL,
  dnl [
  dnl   PHP_ADD_LIBRARY_WITH_PATH($LIBNAME, $JSONPARSER_DIR/$PHP_LIBDIR, JSONPARSER_SHARED_LIBADD)
  dnl   AC_DEFINE(HAVE_JSONPARSER_FEATURE, 1, [ ])
  dnl ],[
  dnl   AC_MSG_ERROR([FEATURE not supported by your jsonparser library.])
  dnl ],[
  dnl   -L$JSONPARSER_DIR/$PHP_LIBDIR -lm
  dnl ])
  dnl
  dnl PHP_SUBST(JSONPARSER_SHARED_LIBADD)

  dnl In case of no dependencies
  AC_DEFINE(HAVE_JSONPARSER, 1, [ Have jsonparser support ])

  PHP_NEW_EXTENSION(jsonparser, jsonparser.c Parser.c, $ext_shared)
fi
