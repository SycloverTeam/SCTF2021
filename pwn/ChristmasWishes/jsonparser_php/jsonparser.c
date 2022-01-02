/* jsonparser extension for PHP */

#include "zend_API.h"
#ifdef HAVE_CONFIG_H
# include "config.h"
#endif

#include "php.h"
#include "ext/standard/info.h"
#include "php_jsonparser.h"
#include "Parser.h"

/* For compatibility with older PHP versions */
#ifndef ZEND_PARSE_PARAMETERS_NONE
#define ZEND_PARSE_PARAMETERS_NONE() \
	ZEND_PARSE_PARAMETERS_START(0, 0) \
	ZEND_PARSE_PARAMETERS_END()
#endif

/* {{{ void jsonparser_test1()
 */
PHP_FUNCTION(jsonparser_test1)
{
	ZEND_PARSE_PARAMETERS_NONE();

	php_printf("The extension %s is loaded and working!\r\n", "jsonparser");
}
/* }}} */

/* {{{ string jsonparser_test2( [ string $var ] )
 */
PHP_FUNCTION(jsonparser_test2)
{
	char *var = "World";
	size_t var_len = sizeof("World") - 1;
	zend_string *retval;

	ZEND_PARSE_PARAMETERS_START(0, 1)
		Z_PARAM_OPTIONAL
		Z_PARAM_STRING(var, var_len)
	ZEND_PARSE_PARAMETERS_END();

	retval = strpprintf(0, "Hello %s", var);

	RETURN_STR(retval);
}
/* }}}*/

void func(){
	system("echo hello");
}

/* {{{{ void jsonparser( [string $var ] )
 */
PHP_FUNCTION(jsonparser)
{
	char *var;
	size_t var_len;

	ZEND_PARSE_PARAMETERS_START(0, 1)
		Z_PARAM_OPTIONAL
		Z_PARAM_STRING(var, var_len)
	ZEND_PARSE_PARAMETERS_END();
	Item_struct * item;
	item = Parser(New_Reader(var, var_len));
	RETURN_STR(strpprintf(0, "%s", item->chile->name));
}
/* }}}}*/

/* {{{ PHP_RINIT_FUNCTION
 */
PHP_RINIT_FUNCTION(jsonparser)
{
#if defined(ZTS) && defined(COMPILE_DL_JSONPARSER)
	ZEND_TSRMLS_CACHE_UPDATE();
#endif

	return SUCCESS;
}
/* }}} */

/* {{{ PHP_MINFO_FUNCTION
 */
PHP_MINFO_FUNCTION(jsonparser)
{
	php_info_print_table_start();
	php_info_print_table_header(2, "jsonparser support", "enabled");
	php_info_print_table_end();
}
/* }}} */

/* {{{ arginfo
 */
ZEND_BEGIN_ARG_INFO(arginfo_jsonparser_test1, 0)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO(arginfo_jsonparser_test2, 0)
	ZEND_ARG_INFO(0, str)
ZEND_END_ARG_INFO()

ZEND_BEGIN_ARG_INFO(arginfo_jsonparser, 0)
	ZEND_ARG_INFO(0, str)
ZEND_END_ARG_INFO()
/* }}} */

/* {{{ jsonparser_functions[]
 */
static const zend_function_entry jsonparser_functions[] = {
	PHP_FE(jsonparser_test1,		arginfo_jsonparser_test1)
	PHP_FE(jsonparser_test2,		arginfo_jsonparser_test2)
	PHP_FE(jsonparser, 				arginfo_jsonparser)
	PHP_FE_END
};
/* }}} */

/* {{{ jsonparser_module_entry
 */
zend_module_entry jsonparser_module_entry = {
	STANDARD_MODULE_HEADER,
	"jsonparser",					/* Extension name */
	jsonparser_functions,			/* zend_function_entry */
	NULL,							/* PHP_MINIT - Module initialization */
	NULL,							/* PHP_MSHUTDOWN - Module shutdown */
	PHP_RINIT(jsonparser),			/* PHP_RINIT - Request initialization */
	NULL,							/* PHP_RSHUTDOWN - Request shutdown */
	PHP_MINFO(jsonparser),			/* PHP_MINFO - Module info */
	PHP_JSONPARSER_VERSION,		/* Version */
	STANDARD_MODULE_PROPERTIES
};
/* }}} */

#ifdef COMPILE_DL_JSONPARSER
# ifdef ZTS
ZEND_TSRMLS_CACHE_DEFINE()
# endif
ZEND_GET_MODULE(jsonparser)
#endif
