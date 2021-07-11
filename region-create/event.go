package regioncreate

import (
	"strings"
	"time"
)

// A structure that represents the rekevant fields of Region Document Snapshot.
// Each field is based on the Value specification: https://firebase.google.com/docs/firestore/reference/rest/v1beta1/Value
type FirestoreFields_Region struct {
	Type struct {
		StringValue string `json:"stringValue"`
	} `json:"type"`

	GeoJSON struct {
		StringValue string `json:"stringValue"`
	} `json:"geojson"`
}

// A structure that reprsents a Document Snapshot
// Specification: https://firebase.google.com/docs/firestore/reference/rest/v1beta1/projects.databases.documents
type FirestoreDocument struct {
	Name       string                 `json:"name"`
	Fields     FirestoreFields_Region `json:"fields"`
	CreateTime time.Time              `json:"createTime"`
	UpdateTime time.Time              `json:"updateTime"`
}

// A structure that represents a Cloud Firestore Event
// Specification: https://cloud.google.com/functions/docs/calling/cloud-firestore#event_structure
type FirestoreEvent struct {
	Value      FirestoreDocument `json:"value"`
	OldValue   FirestoreDocument `json:"oldValue"`
	UpdateMask struct {
		FieldPaths []string `json:"fieldPaths"`
	} `json:"updateMask"`
}

// A method of FirestoreEvent that retrieves the path of the document from the event trigger.
func (event *FirestoreEvent) getDocPath() string {
	splitpath := strings.Split(event.Value.Name, "documents/")
	return splitpath[len(splitpath)-1]
}
