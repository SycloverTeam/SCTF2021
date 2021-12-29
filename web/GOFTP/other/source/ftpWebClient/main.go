package main

import (
	. "WebFTPClient/config"
	. "WebFTPClient/route"

	"github.com/gin-contrib/sessions"
	"github.com/gin-contrib/sessions/cookie"
	"github.com/gin-gonic/gin"
)

func main() {
	webapp := gin.Default()
	store := cookie.NewStore([]byte(AppConfig.Session.Secret))

	webapp.Use(sessions.Sessions(AppConfig.Session.Name, store))
	webapp.Use(gin.Recovery())

	webapp.LoadHTMLGlob("view/*")
	webapp.Static("/assets", "./assets")

	SetRoute(webapp)
	webapp.Run(":" + AppConfig.App.Port)
}
