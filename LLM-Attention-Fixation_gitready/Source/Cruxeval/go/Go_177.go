package main

import (
    "fmt"
    "testing"
)

func f(text string) string {
	newText := []rune(text)
	for i := 0; i < len(newText); i++ {
		if i%2 == 1 {
			if newText[i] >= 'a' && newText[i] <= 'z' {
				newText[i] -= 32
			} else if newText[i] >= 'A' && newText[i] <= 'Z' {
				newText[i] += 32
			}
		}
	}
	return string(newText)
}

func main() {
	text := "Hello, World!"
	fmt.Println(f(text))
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Hey DUdE THis $nd^ &*&this@#"), expected: "HEy Dude tHIs $Nd^ &*&tHiS@#" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
