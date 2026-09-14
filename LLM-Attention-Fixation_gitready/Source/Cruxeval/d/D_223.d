import std.math;
import std.typecons;
long f(long[] array, long target) 
{
    long count = 0;
    long i = 1;
    for (size_t j = 1; j < array.length; j++) {
        if ((array[j] > array[j-1]) && (array[j] <= target)) {
            count += i;
        } else if (array[j] <= array[j-1]) {
            i = 1;
        } else {
            i += 1;
        }
    }
    return count;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, -1L, 4L], 2L) == 1L);
}
void main(){}
