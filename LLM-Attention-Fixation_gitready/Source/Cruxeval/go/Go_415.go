package main

import (
    "fmt"
    "testing"
)

func f(array []interface{}) map[int]int {
	d := make(map[int]int)
	for i := 0; i < len(array); i++ {
		pair := array[i].([]interface{})
		key := pair[0].(int)
		value := pair[1].(int)
		d[key] = value
	}
	for _, value := range d {
		if value < 0 || value > 9 {
			return nil
		}
	}
	return d
}

func main() {
	array := []interface{}{
		[]interface{}{1, 5},
		[]interface{}{2, 8},
		[]interface{}{3, 3},
	}
	result := f(array)
	fmt.Println(result)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]interface{}{[]interface{}{8, 5}, []interface{}{8, 2}, []interface{}{5, 3}}), expected: map[int]int{8: 2, 5: 3} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
