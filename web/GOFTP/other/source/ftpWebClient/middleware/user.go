package middleware

import (
	"strings"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
)

func UserSessionCheck(c *gin.Context) {
	sess := sessions.Default(c)
	if sess.Get("username") == nil {
		c.HTML(403, "forbidden.html", gin.H{})
		c.Abort()
		return
	}
	c.Next()
}

func AdminSessionCheck(c *gin.Context) {
	sess := sessions.Default(c)

	username, ok := sess.Get("username").(string)
	if !ok || !strings.EqualFold(username, "admin") {
		c.HTML(403, "forbidden.html", gin.H{})
		c.Abort()
		return
	}
	c.Next()
}
