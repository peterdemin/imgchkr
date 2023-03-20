package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"

	"github.com/google/uuid"
	"github.com/gorilla/mux"
)

// ImageValidationRequest defines the payload for image validation
type ImageValidationRequest struct {
	AssetPath struct {
		Location string `json:"location"`
		Path     string `json:"path"`
	} `json:"assetPath"`
	Notifications struct {
		OnStart   string `json:"onStart"`
		OnSuccess string `json:"onSuccess"`
		OnFailure string `json:"onFailure"`
	} `json:"notifications"`
}

// ImageValidationResponse defines the response to send after receiving an image validation request
type ImageValidationResponse struct {
	ID    uuid.UUID `json:"id"`
	State string    `json:"state"`
}

func main() {
	router := mux.NewRouter()
	router.HandleFunc("/assets/image", handleImageValidation).Methods("POST")
	router.HandleFunc("/assets/image/{id}", handleStatus).Methods("GET")

	if err := http.ListenAndServe(":5001", router); err != nil {
		panic(err)
	}
}

func handleImageValidation(w http.ResponseWriter, r *http.Request) {
	var req ImageValidationRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	response := ImageValidationResponse{
		ID:    uuid.New(),
		State: "queued",
	}

	go processImageValidation(req, response)

	logImageValidationRequest(req)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	json.NewEncoder(w).Encode(response)
}

func logImageValidationRequest(req ImageValidationRequest) {
	reqJSON, err := json.MarshalIndent(req, "", "  ")
	if err != nil {
		fmt.Println("Error marshalling ImageValidationRequest:", err)
		return
	}
	fmt.Println("ImageValidationRequest:")
	fmt.Println(string(reqJSON))
}

func handleStatus(w http.ResponseWriter, r *http.Request) {
	// Replace this with your implementation to fetch the status of a queued submission.
}

func processImageValidation(req ImageValidationRequest, response ImageValidationResponse) {
	// Replace this with your implementation to validate the image file and send notifications.

	if err := postJSON(req.Notifications.OnStart, response); err != nil {
		fmt.Println(err)
	}
	if fileExists(req.AssetPath.Path) {
        response.State = "success"
        if err := postJSON(req.Notifications.OnSuccess, response); err != nil {
            fmt.Println(err)
        }
    } else {
        response.State = "failed"
        if err := postJSON(req.Notifications.OnFailure, response); err != nil {
            fmt.Println(err)
        }
    }
}

func fileExists(filepath string) bool {
	_, err := os.Stat(filepath)
	if os.IsNotExist(err) {
		return false
	}
	return err == nil
}

func postJSON(url string, payload interface{}) error {
	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("error marshalling JSON payload: %v", err)
	}

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(payloadBytes))
	if err != nil {
		return fmt.Errorf("error making HTTP POST request: %v", err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("error reading HTTP response body: %v", err)
	}

	fmt.Printf("Status Code: %d\n", resp.StatusCode)
	fmt.Printf("Response Body: %s\n", string(body))

	return nil
}
