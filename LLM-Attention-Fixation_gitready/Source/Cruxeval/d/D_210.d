import std.math;
import std.typecons;
import std.range;

long f(long n, long m, long num) 
{
    auto x_list = new long[](m - n + 1);
    foreach (i; 0 .. x_list.length) {
        x_list[i] = n + i;
    }
    
    long j = 0;
    while (true) {
        j = (j + num) % x_list.length;
        if (x_list[j] % 2 == 0) {
            return x_list[j];
        }
    }
}
unittest
{
    alias candidate = f;

    assert(candidate(46L, 48L, 21L) == 46L);
}
void main(){}
