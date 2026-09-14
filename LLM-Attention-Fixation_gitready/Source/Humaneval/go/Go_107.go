import (
    "strconv"
)

// Given a positive integer n, return a tuple that has the number of even and odd
// integer palindromes that fall within the range(1, n), inclusive.
// 
// Example 1:
// 
// Input: 3
// Output: (1, 2)
// Explanation:
// Integer palindrome are 1, 2, 3. one of them is even, and two of them are odd.
// 
// Example 2:
// 
// Input: 12
// Output: (4, 6)
// Explanation:
// Integer palindrome are 1, 2, 3, 4, 5, 6, 7, 8, 9, 11. four of them are even, and 6 of them are odd.
// 
// Note:
// 1. 1 <= n <= 10^3
// 2. returned tuple has the number of even and odd integer palindromes respectively.
func EvenOddPalindrome(n int) [2]int {

    is_palindrome := func (n int) bool {
        s := strconv.Itoa(n)
        for i := 0;i < len(s)>>1;i++ {
            if s[i] != s[len(s)-i-1] {
                return false
            }
        }
        return true
    }

    even_palindrome_count := 0
    odd_palindrome_count := 0

    for i :=1;i<n+1;i++ {
        if i%2 == 1 && is_palindrome(i){
                odd_palindrome_count ++
        } else if i%2 == 0 && is_palindrome(i) {
            even_palindrome_count ++
        }
    }
    return [2]int{even_palindrome_count, odd_palindrome_count}
}

func TestEvenOddPalindrome(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([2]int{8,13}, EvenOddPalindrome(123))
    assert.Equal([2]int{4,6}, EvenOddPalindrome(12))
    assert.Equal([2]int{1,2}, EvenOddPalindrome(3))
    assert.Equal([2]int{6,8}, EvenOddPalindrome(63))
    assert.Equal([2]int{5,6}, EvenOddPalindrome(25))
    assert.Equal([2]int{4,6}, EvenOddPalindrome(19))
    assert.Equal([2]int{4,5}, EvenOddPalindrome(9))
    assert.Equal([2]int{0,1}, EvenOddPalindrome(1))
}
