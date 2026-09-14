import std.math;
import std.typecons;
import std.ascii;

long f(string string) 
{
    long upper = 0;
    foreach (c; string) {
        if (std.ascii.isUpper(c)) {
            upper += 1;
        }
    }
    return upper * [2, 1][upper % 2];
}
unittest
{
    alias candidate = f;

    assert(candidate("PoIOarTvpoead") == 8L);
}
void main(){}
