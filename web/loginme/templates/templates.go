package templates

import "embed"

//go:embed admin_index.tmpl
var AdminIndexTemplateHtml string

//go:embed *
var Templates embed.FS
