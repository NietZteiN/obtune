import std.math;
import std.typecons;

long[] f(long[] lst) 
{
    for (int i = cast(int)(lst.length - 1); i > 0; i--) {
        for (int j = 0; j < i; j++) {
            if (lst[j] > lst[j + 1]) {
                auto temp = lst[j];
                lst[j] = lst[j + 1];
                lst[j + 1] = temp;
            }
        }
    }
    return lst;
}
unittest
{
    alias candidate = f;

    assert(candidate([63L, 0L, 1L, 5L, 9L, 87L, 0L, 7L, 25L, 4L]) == [0L, 0L, 1L, 4L, 5L, 7L, 9L, 25L, 63L, 87L]);
}
void main(){}
