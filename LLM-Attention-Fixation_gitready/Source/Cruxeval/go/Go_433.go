package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	texts := strings.Split(text, ",")
	texts = append(texts[:0], texts[1:]...)
	tIndex := -1
	for i, v := range texts {
		if v == "T" {
			tIndex = i
			break
		}
	}
	if tIndex != -1 {
		first := texts[tIndex]
		texts = append(texts[:tIndex], texts[tIndex+1:]...)
		texts = append([]string{first}, texts...)
	}
	return "T" + "," + strings.Join(texts, ",")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Dmreh,Sspp,T,G ,.tB,Vxk,Cct"), expected: "T,T,Sspp,G ,.tB,Vxk,Cct" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
