package model

import (
	. "WebFTPClient/config"
	"encoding/json"

	req "github.com/levigross/grequests"
)

type ApiResp struct {
	Value string
	Data  interface{}
}

func encodeResp(resp *req.Response) (*ApiResp, error) {
	data := new(ApiResp)
	rawData := resp.Bytes()
	err := json.Unmarshal(rawData, &data)
	if err != nil {
		return nil, err
	}

	return data, err
}

func AuthUser(email string, passwd string) (map[string]interface{}, bool) {
	opt := &req.RequestOptions{
		Params: map[string]string{
			"email":    email,
			"password": passwd,
		},
	}

	resp, err := req.Get(AppConfig.Api.Addr+"/api/user", opt)
	if err != nil {
		return nil, false
	}

	data, err := encodeResp(resp)
	if err != nil {
		return nil, false
	}

	if data.Data != false {
		return data.Data.(map[string]interface{}), true
	} else {
		return nil, false
	}
}

func CreateUser(email string, username string, password string) (string, bool) {
	opt := &req.RequestOptions{
		JSON: map[string]string{
			"email":    email,
			"username": username,
			"password": password,
		},
	}

	resp, err := req.Put(AppConfig.Api.Addr+"/api/user", opt)
	if err != nil {
		return "API Client Error", false
	}

	data, err := encodeResp(resp)
	if err != nil {
		return "RESP Encode Error", false
	}

	return data.Value, data.Data.(bool)
}
