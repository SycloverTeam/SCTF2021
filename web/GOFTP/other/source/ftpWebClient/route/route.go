package route

import (
	"WebFTPClient/controller"
	"WebFTPClient/middleware"

	"github.com/gin-gonic/gin"
)

func SetRoute(app *gin.Engine) {
	app.GET("/", controller.Index)
	app.GET("/index", controller.Index)
	app.GET("/login", controller.LoginPage)
	app.GET("/register", controller.RegisterPage)

	api := app.Group("/api")
	api.GET("/logout", controller.Logout)
	api.POST("/login", controller.Login)
	api.POST("/register", controller.Register)

	normalUser := app.Group("/")
	normalUser.Use(middleware.UserSessionCheck)
	normalUser.GET("/upload", controller.UploadPage)

	normalUserApi := normalUser.Group("/api")
	normalUserApi.POST("/upload", controller.Upload)

	adminUser := normalUser.Group("/admin")
	adminUser.Use(middleware.AdminSessionCheck)
	adminUser.GET("", controller.ShowSecretPage)
	adminUser.GET("/index", controller.ShowSecretPage)

	adminUserApi := adminUser.Group("/api")
	adminUserApi.POST("/addAdmin", controller.AddAdminUser)
}
