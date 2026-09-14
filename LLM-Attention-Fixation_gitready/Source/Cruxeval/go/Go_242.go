package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(book string) string {
    a := strings.Split(book, ":")
    if strings.Fields(a[0])[len(strings.Fields(a[0]))-1] == strings.Fields(a[1])[0] {
        return f(strings.Join(strings.Fields(a[0])[:len(strings.Fields(a[0]))-1], " ") + " " + a[1])
    }
    return book
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("udhv zcvi nhtnfyd :erwuyawa pun"), expected: "udhv zcvi nhtnfyd :erwuyawa pun" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
