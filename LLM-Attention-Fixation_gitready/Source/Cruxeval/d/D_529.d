import std.math;
import std.typecons;
long[] f(long[] array) 
{
    if (array.length == 0) {
        return [];
    }

    long prev = array[0];
    long[] newArray = array.dup;

    for (size_t i = 1; i < array.length; i++) {
        if (prev != array[i]) {
            newArray[i] = array[i];
        } else {
            newArray = newArray[0 .. i] ~ newArray[i + 1 .. $];
            i--;
        }
        prev = array[i];
    }

    return newArray;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L]) == [1L, 2L, 3L]);
}
void main(){}
