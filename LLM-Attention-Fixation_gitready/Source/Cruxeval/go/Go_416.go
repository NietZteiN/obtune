package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, old string, new string) string {
	index := strings.LastIndex(text[:strings.Index(text, old)], old)
	result := []rune(text)
	for index > 0 {
		result = append(result[:index], append([]rune(new), result[index+len(old):]...)...)
		index = strings.LastIndex(text[:index], old)
	}
	return string(result)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("jysrhfm ojwesf xgwwdyr dlrul ymba bpq", "j", "1"), expected: "jysrhfm ojwesf xgwwdyr dlrul ymba bpq" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
