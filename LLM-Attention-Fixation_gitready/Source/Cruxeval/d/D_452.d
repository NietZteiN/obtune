import std.math;
import std.typecons;
import std.ascii;

long f(string text) 
{
    long counter = 0;
    foreach (char c; text) {
        if (isAlpha(c)) {
            counter++;
        }
    }
    return counter;
}
unittest
{
    alias candidate = f;

    assert(candidate("l000*") == 1L);
}
void main(){}
