
// Imagine a road that's a perfectly straight infinitely long line.
// n cars are driving left to right;  simultaneously, a different set of n cars
// are driving right to left.   The two sets of cars start out being very far from
// each other.  All cars move in the same speed.  Two cars are said to collide
// when a car that's moving left to right hits a car that's moving right to left.
// However, the cars are infinitely sturdy and strong; as a result, they continue moving
// in their trajectory as if they did not collide.
// 
// This function outputs the number of such collisions.
func CarRaceCollision(n int) int {

	return n * n
}

func TestCarRaceCollision(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(4, CarRaceCollision(2))
    assert.Equal(9, CarRaceCollision(3))
    assert.Equal(16, CarRaceCollision(4))
    assert.Equal(64, CarRaceCollision(8))
    assert.Equal(100, CarRaceCollision(10))
}
