package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
    arr := strings.Split(text, " ")
    var result []string
    for _, item := range arr {
        if strings.HasSuffix(item, "day") {
            item += "y"
        } else {
            item += "day"
        }
        result = append(result, item)
    }
    return strings.Join(result, " ")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("nwv mef ofme bdryl"), expected: "nwvday mefday ofmeday bdrylday" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
