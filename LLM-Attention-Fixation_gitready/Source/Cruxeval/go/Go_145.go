package main

import (
    "fmt"
    "testing"
)

func f(price float64, product string) float64 {
	inventory := []string{"olives", "key", "orange"}
	if !contains(inventory, product) {
		return price
	} else {
		price *= 0.85
		inventory = removeElement(inventory, product)
	}
	return price
}

func contains(arr []string, str string) bool {
	for _, a := range arr {
		if a == str {
			return true
		}
	}
	return false
}

func removeElement(arr []string, str string) []string {
	index := -1
	for i, a := range arr {
		if a == str {
			index = i
			break
		}
	}
	if index != -1 {
		arr = append(arr[:index], arr[index+1:]...)
	}
	return arr
}

func main() {
	price := 100.0
	product := "olives"
	fmt.Println(f(price, product))
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(8.5, "grapes"), expected: 8.5 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
