
// Write a function that takes a string and returns true if the string
// length is a prime number or false otherwise
// Examples
// PrimeLength('Hello') == true
// PrimeLength('abcdcba') == true
// PrimeLength('kittens') == true
// PrimeLength('orange') == false
func PrimeLength(s string) bool {

    l := len(s)
    if l == 0 || l == 1 {
        return false
    }
    for i := 2; i < l; i++ {
        if l%i == 0 {
            return false
        }
    }
    return true
}

func TestPrimeLength(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(true, PrimeLength("Hello"))
    assert.Equal(true, PrimeLength("abcdcba"))
    assert.Equal(true, PrimeLength("kittens"))
    assert.Equal(false, PrimeLength("orange"))
    assert.Equal(true, PrimeLength("wow"))
    assert.Equal(true, PrimeLength("world"))
    assert.Equal(true, PrimeLength("MadaM"))
    assert.Equal(true, PrimeLength("Wow"))
    assert.Equal(false, PrimeLength(""))
    assert.Equal(true, PrimeLength("HI"))
    assert.Equal(true, PrimeLength("go"))
    assert.Equal(false, PrimeLength("gogo"))
    assert.Equal(false, PrimeLength("aaaaaaaaaaaaaaa"))
    assert.Equal(true, PrimeLength("Madam"))
    assert.Equal(false, PrimeLength("M"))
    assert.Equal(false, PrimeLength("0"))
}
