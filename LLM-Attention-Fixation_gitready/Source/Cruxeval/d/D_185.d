import std.math;
import std.typecons;
long[] f(long[] L) 
{
    auto N = L.length;
    foreach (k; 1 .. N / 2 + 1) {
        auto i = k - 1;
        auto j = N - k;
        while (i < j) {
            // swap elements:
            L[i] = L[i] + L[j];
            L[j] = L[i] - L[j];
            L[i] = L[i] - L[j];
            // update i, j:
            i++;
            j--;
        }
    }
    return L;
}
unittest
{
    alias candidate = f;

    assert(candidate([16L, 14L, 12L, 7L, 9L, 11L]) == [11L, 14L, 7L, 12L, 9L, 16L]);
}
void main(){}
