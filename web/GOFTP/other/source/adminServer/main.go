package main

import (
	. "adminServer/config"
	. "adminServer/model"
	. "adminServer/route"
	"log"

	"github.com/gin-gonic/gin"
)

func main() {
	webapp := gin.Default()

	dsn := WebAppConfig.DB.Username + ":" +
		   WebAppConfig.DB.Password + "@" + 
		   "tcp(" + WebAppConfig.DB.Address + ")/" + 
		   WebAppConfig.DB.Database
		   
	if err := Connect(dsn); err != nil {
		log.Fatalln("Mysql Connect Error: " + err.Error())
	}
	defer Close()

	SetAdminRoute(webapp)
	webapp.Run(":" + WebAppConfig.App.Port)
}
