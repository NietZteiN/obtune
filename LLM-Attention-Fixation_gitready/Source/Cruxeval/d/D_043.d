import std.math;
import std.typecons;
import std.ascii;
import std.conv;

long f(string n) 
{
    foreach (i; n) {
        if (!isDigit(i)) {
            return -1;
        }
    }
    return to!int(n);
}
unittest
{
    alias candidate = f;

    assert(candidate("6 ** 2") == -1L);
}
void main(){}
